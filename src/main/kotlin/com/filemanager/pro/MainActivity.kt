package com.filemanager.pro

import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.button.MaterialButton
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File

class MainActivity : AppCompatActivity() {

    private val PERMISSION_REQUEST_CODE = 100
    private lateinit var recyclerView: RecyclerView
    private lateinit var fileAdapter: FileAdapter
    private var currentPath: String = "/storage/emulated/0"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        setupUI()
        checkPermissions()
    }

    private fun setupUI() {
        recyclerView = findViewById(R.id.recyclerView)
        fileAdapter = FileAdapter { file -> onFileSelected(file) }
        recyclerView.layoutManager = LinearLayoutManager(this)
        recyclerView.adapter = fileAdapter

        findViewById<MaterialButton>(R.id.btnHome).setOnClickListener {
            currentPath = "/storage/emulated/0"
            loadFiles()
        }

        loadFiles()
    }

    private fun checkPermissions() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_EXTERNAL_STORAGE)
                != PackageManager.PERMISSION_GRANTED
            ) {
                ActivityCompat.requestPermissions(
                    this,
                    arrayOf(
                        Manifest.permission.READ_EXTERNAL_STORAGE,
                        Manifest.permission.MANAGE_EXTERNAL_STORAGE
                    ),
                    PERMISSION_REQUEST_CODE
                )
            }
        }
    }

    private fun loadFiles() {
        lifecycleScope.launch {
            try {
                val files = withContext(Dispatchers.IO) {
                    getFiles(currentPath)
                }
                fileAdapter.submitList(files)
            } catch (e: Exception) {
                Toast.makeText(this@MainActivity, "خطأ: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun getFiles(path: String): List<File> {
        return try {
            val dir = File(path)
            if (dir.exists() && dir.isDirectory) {
                dir.listFiles()?.sortedWith(compareBy({ !it.isDirectory }, { it.name }))
                    ?.toList() ?: emptyList()
            } else {
                emptyList()
            }
        } catch (e: Exception) {
            emptyList()
        }
    }

    private fun onFileSelected(file: File) {
        if (file.isDirectory) {
            currentPath = file.absolutePath
            loadFiles()
        } else {
            Toast.makeText(this, "تم فتح: ${file.name}", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == PERMISSION_REQUEST_CODE && grantResults.isNotEmpty()) {
            if (grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                loadFiles()
            }
        }
    }
}