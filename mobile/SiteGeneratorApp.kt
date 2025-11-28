// Phone App: Complete Authority Site Generator
// Kotlin + Jetpack Compose

// ============================================================
// API Client
// ============================================================

interface SiteGeneratorAPI {
    @Multipart
    @POST("/api/generate-site")
    suspend fun generateSite(
        @Part resume: MultipartBody.Part,
        @Part("specialty") specialty: RequestBody,
        @Part("yearsExperience") yearsExperience: RequestBody,
        @Part("majorAchievement") majorAchievement: RequestBody,
        @Part credentialsPhoto: MultipartBody.Part? = null
    ): GenerateSiteResponse
    
    @GET("/api/check-status")
    suspend fun checkStatus(@Query("jobId") jobId: String): JobStatusResponse
    
    companion object {
        fun create(): SiteGeneratorAPI {
            val retrofit = Retrofit.Builder()
                .baseUrl("https://your-worker.workers.dev")
                .addConverterFactory(GsonConverterFactory.create())
                .build()
            
            return retrofit.create(SiteGeneratorAPI::class.java)
        }
    }
}

data class GenerateSiteResponse(
    val jobId: String,
    val status: String,
    val message: String
)

data class JobStatusResponse(
    val status: String, // "processing", "complete", "failed"
    val siteUrl: String? = null,
    val error: String? = null
)

// ============================================================
// View Model
// ============================================================

class SiteGeneratorViewModel : ViewModel() {
    private val api = SiteGeneratorAPI.create()
    
    private val _uiState = MutableStateFlow<UiState>(UiState.Initial)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()
    
    sealed class UiState {
        object Initial : UiState()
        object Uploading : UiState()
        data class Processing(val progress: Int) : UiState()
        data class Success(val siteUrl: String) : UiState()
        data class Error(val message: String) : UiState()
    }
    
    fun generateSite(
        resumeUri: Uri,
        specialty: String,
        yearsExperience: String,
        majorAchievement: String,
        photoUri: Uri? = null,
        context: Context
    ) {
        viewModelScope.launch {
            try {
                _uiState.value = UiState.Uploading
                
                // Prepare resume file
                val resumeFile = uriToFile(resumeUri, context)
                val resumePart = MultipartBody.Part.createFormData(
                    "resume",
                    resumeFile.name,
                    resumeFile.asRequestBody("application/octet-stream".toMediaType())
                )
                
                // Prepare photo (optional)
                val photoPart = photoUri?.let { uri ->
                    val photoFile = uriToFile(uri, context)
                    MultipartBody.Part.createFormData(
                        "credentialsPhoto",
                        photoFile.name,
                        photoFile.asRequestBody("image/*".toMediaType())
                    )
                }
                
                // Submit generation request
                val response = api.generateSite(
                    resume = resumePart,
                    specialty = specialty.toRequestBody("text/plain".toMediaType()),
                    yearsExperience = yearsExperience.toRequestBody("text/plain".toMediaType()),
                    majorAchievement = majorAchievement.toRequestBody("text/plain".toMediaType()),
                    credentialsPhoto = photoPart
                )
                
                // Poll for completion
                _uiState.value = UiState.Processing(0)
                pollStatus(response.jobId)
                
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }
    
    private suspend fun pollStatus(jobId: String) {
        var attempts = 0
        val maxAttempts = 30 // 30 seconds max (2 sec intervals)
        
        while (attempts < maxAttempts) {
            delay(2000) // Wait 2 seconds
            attempts++
            
            val progress = (attempts * 100) / maxAttempts
            _uiState.value = UiState.Processing(progress)
            
            try {
                val status = api.checkStatus(jobId)
                
                when (status.status) {
                    "complete" -> {
                        _uiState.value = UiState.Success(status.siteUrl!!)
                        return
                    }
                    "failed" -> {
                        _uiState.value = UiState.Error(
                            status.error ?: "Site generation failed"
                        )
                        return
                    }
                    "processing" -> {
                        // Continue polling
                    }
                }
                
            } catch (e: Exception) {
                // Continue polling on network errors
                Log.e("SiteGenerator", "Poll error: ${e.message}")
            }
        }
        
        _uiState.value = UiState.Error("Timeout waiting for site generation")
    }
    
    private fun uriToFile(uri: Uri, context: Context): File {
        val contentResolver = context.contentResolver
        val file = File(context.cacheDir, "upload_${System.currentTimeMillis()}")
        
        contentResolver.openInputStream(uri)?.use { input ->
            file.outputStream().use { output ->
                input.copyTo(output)
            }
        }
        
        return file
    }
}

// ============================================================
// UI Screens
// ============================================================

@Composable
fun SiteGeneratorFlow(
    navController: NavController,
    viewModel: SiteGeneratorViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    when (uiState) {
        is SiteGeneratorViewModel.UiState.Initial -> {
            UploadScreen(viewModel)
        }
        is SiteGeneratorViewModel.UiState.Uploading -> {
            ProcessingScreen("Uploading resume...", 0)
        }
        is SiteGeneratorViewModel.UiState.Processing -> {
            val progress = (uiState as SiteGeneratorViewModel.UiState.Processing).progress
            ProcessingScreen("Generating your authority site...", progress)
        }
        is SiteGeneratorViewModel.UiState.Success -> {
            val url = (uiState as SiteGeneratorViewModel.UiState.Success).siteUrl
            SuccessScreen(url, navController)
        }
        is SiteGeneratorViewModel.UiState.Error -> {
            val message = (uiState as SiteGeneratorViewModel.UiState.Error).message
            ErrorScreen(message, viewModel)
        }
    }
}

@Composable
fun UploadScreen(viewModel: SiteGeneratorViewModel) {
    val context = LocalContext.current
    
    var resumeUri by remember { mutableStateOf<Uri?>(null) }
    var photoUri by remember { mutableStateOf<Uri?>(null) }
    var specialty by remember { mutableStateOf("") }
    var yearsExperience by remember { mutableStateOf("") }
    var majorAchievement by remember { mutableStateOf("") }
    
    val resumeLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        resumeUri = uri
    }
    
    val photoLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.TakePicture()
    ) { success ->
        if (success) {
            // Photo saved to photoUri
        }
    }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp)
            .verticalScroll(rememberScrollState()),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Header
        Text(
            text = "Generate Your Authority Site",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            textAlign = TextAlign.Center
        )
        
        Text(
            text = "Upload your resume and we'll create a professional website in 30 seconds",
            style = MaterialTheme.typography.bodyMedium,
            color = Color.Gray,
            textAlign = TextAlign.Center,
            modifier = Modifier.padding(top = 8.dp, bottom = 32.dp)
        )
        
        // Resume upload
        OutlinedCard(
            modifier = Modifier
                .fillMaxWidth()
                .clickable { resumeLauncher.launch("application/*") },
            colors = CardDefaults.outlinedCardColors(
                containerColor = if (resumeUri != null) 
                    MaterialTheme.colorScheme.primaryContainer 
                else 
                    Color.Transparent
            )
        ) {
            Row(
                modifier = Modifier.padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = if (resumeUri != null) 
                        Icons.Default.CheckCircle 
                    else 
                        Icons.Default.Upload,
                    contentDescription = null,
                    modifier = Modifier.size(40.dp)
                )
                
                Column(modifier = Modifier.padding(start = 16.dp)) {
                    Text(
                        text = if (resumeUri != null) 
                            "Resume uploaded ✓" 
                        else 
                            "Upload Resume",
                        style = MaterialTheme.typography.titleMedium
                    )
                    Text(
                        text = "PDF, DOCX, or TXT",
                        style = MaterialTheme.typography.bodySmall,
                        color = Color.Gray
                    )
                }
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Optional photo
        OutlinedCard(
            modifier = Modifier
                .fillMaxWidth()
                .clickable { 
                    val uri = createImageUri(context)
                    photoUri = uri
                    photoLauncher.launch(uri)
                },
            colors = CardDefaults.outlinedCardColors(
                containerColor = if (photoUri != null) 
                    MaterialTheme.colorScheme.secondaryContainer 
                else 
                    Color.Transparent
            )
        ) {
            Row(
                modifier = Modifier.padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = Icons.Default.CameraAlt,
                    contentDescription = null,
                    modifier = Modifier.size(40.dp)
                )
                
                Column(modifier = Modifier.padding(start = 16.dp)) {
                    Text(
                        text = if (photoUri != null) 
                            "Photo added ✓" 
                        else 
                            "Photo of Credentials (Optional)",
                        style = MaterialTheme.typography.titleMedium
                    )
                    Text(
                        text = "Certificates, awards, etc.",
                        style = MaterialTheme.typography.bodySmall,
                        color = Color.Gray
                    )
                }
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Questions
        OutlinedTextField(
            value = specialty,
            onValueChange = { specialty = it },
            label = { Text("Your Specialty") },
            placeholder = { Text("e.g., Clinical Operations") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        OutlinedTextField(
            value = yearsExperience,
            onValueChange = { yearsExperience = it },
            label = { Text("Years of Experience") },
            placeholder = { Text("e.g., 15") },
            modifier = Modifier.fillMaxWidth(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            singleLine = true
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        OutlinedTextField(
            value = majorAchievement,
            onValueChange = { majorAchievement = it },
            label = { Text("Your Biggest Achievement") },
            placeholder = { Text("e.g., Rescued $50M clinical trial") },
            modifier = Modifier.fillMaxWidth(),
            minLines = 2,
            maxLines = 3
        )
        
        Spacer(modifier = Modifier.height(32.dp))
        
        // Generate button
        Button(
            onClick = {
                resumeUri?.let { uri ->
                    viewModel.generateSite(
                        resumeUri = uri,
                        specialty = specialty,
                        yearsExperience = yearsExperience,
                        majorAchievement = majorAchievement,
                        photoUri = photoUri,
                        context = context
                    )
                }
            },
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp),
            enabled = resumeUri != null && 
                      specialty.isNotBlank() && 
                      yearsExperience.isNotBlank()
        ) {
            Icon(Icons.Default.Rocket, contentDescription = null)
            Spacer(modifier = Modifier.width(8.dp))
            Text("Generate My Site (30 sec)")
        }
    }
}

@Composable
fun ProcessingScreen(message: String, progress: Int) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        CircularProgressIndicator(
            modifier = Modifier.size(80.dp),
            strokeWidth = 8.dp
        )
        
        Spacer(modifier = Modifier.height(32.dp))
        
        Text(
            text = message,
            style = MaterialTheme.typography.titleLarge,
            textAlign = TextAlign.Center
        )
        
        if (progress > 0) {
            Spacer(modifier = Modifier.height(16.dp))
            
            LinearProgressIndicator(
                progress = progress / 100f,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(8.dp)
            )
            
            Text(
                text = "$progress%",
                style = MaterialTheme.typography.bodyMedium,
                color = Color.Gray,
                modifier = Modifier.padding(top = 8.dp)
            )
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        Text(
            text = "AI is analyzing your resume and generating your professional website...",
            style = MaterialTheme.typography.bodyMedium,
            color = Color.Gray,
            textAlign = TextAlign.Center
        )
    }
}

@Composable
fun SuccessScreen(siteUrl: String, navController: NavController) {
    val context = LocalContext.current
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = Icons.Default.CheckCircle,
            contentDescription = null,
            tint = Color(0xFF4CAF50),
            modifier = Modifier.size(120.dp)
        )
        
        Spacer(modifier = Modifier.height(32.dp))
        
        Text(
            text = "🎉 Your Authority Site is Live!",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            textAlign = TextAlign.Center
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        OutlinedCard(
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "Your URL",
                    style = MaterialTheme.typography.labelMedium,
                    color = Color.Gray
                )
                
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = siteUrl,
                        style = MaterialTheme.typography.bodyLarge,
                        modifier = Modifier.weight(1f)
                    )
                    
                    IconButton(onClick = {
                        copyToClipboard(context, siteUrl)
                        Toast.makeText(context, "URL copied!", Toast.LENGTH_SHORT).show()
                    }) {
                        Icon(Icons.Default.ContentCopy, contentDescription = "Copy")
                    }
                }
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        Button(
            onClick = {
                openBrowser(context, siteUrl)
            },
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp)
        ) {
            Icon(Icons.Default.OpenInBrowser, contentDescription = null)
            Spacer(modifier = Modifier.width(8.dp))
            Text("View My Site")
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        OutlinedButton(
            onClick = {
                shareUrl(context, siteUrl)
            },
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp)
        ) {
            Icon(Icons.Default.Share, contentDescription = null)
            Spacer(modifier = Modifier.width(8.dp))
            Text("Share Link")
        }
        
        Spacer(modifier = Modifier.height(32.dp))
        
        TextButton(onClick = {
            navController.popBackStack()
        }) {
            Text("Generate Another Site")
        }
    }
}

@Composable
fun ErrorScreen(message: String, viewModel: SiteGeneratorViewModel) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = Icons.Default.Error,
            contentDescription = null,
            tint = Color.Red,
            modifier = Modifier.size(80.dp)
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        Text(
            text = "Generation Failed",
            style = MaterialTheme.typography.titleLarge
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Text(
            text = message,
            style = MaterialTheme.typography.bodyMedium,
            color = Color.Gray,
            textAlign = TextAlign.Center
        )
        
        Spacer(modifier = Modifier.height(32.dp))
        
        Button(onClick = {
            // Reset to initial state
            viewModel.resetState()
        }) {
            Text("Try Again")
        }
    }
}

// ============================================================
// Utility Functions
// ============================================================

fun createImageUri(context: Context): Uri {
    val imageFile = File(context.cacheDir, "photo_${System.currentTimeMillis()}.jpg")
    return FileProvider.getUriForFile(
        context,
        "${context.packageName}.fileprovider",
        imageFile
    )
}

fun openBrowser(context: Context, url: String) {
    val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
    context.startActivity(intent)
}

fun shareUrl(context: Context, url: String) {
    val intent = Intent(Intent.ACTION_SEND).apply {
        type = "text/plain"
        putExtra(Intent.EXTRA_TEXT, "Check out my authority site: $url")
    }
    context.startActivity(Intent.createChooser(intent, "Share via"))
}

fun copyToClipboard(context: Context, text: String) {
    val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
    val clip = ClipData.newPlainText("URL", text)
    clipboard.setPrimaryClip(clip)
}
