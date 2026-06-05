package com.filemanager.pro

import android.view.LayoutInflater
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class FileAdapter(
    private val onFileClick: (File) -> Unit
) : ListAdapter<File, FileAdapter.FileViewHolder>(FileDiffCallback()) {

    inner class FileViewHolder(itemView: android.view.View) : RecyclerView.ViewHolder(itemView) {
        private val fileName = itemView.findViewById<TextView>(android.R.id.text1)
        private val fileInfo = itemView.findViewById<TextView>(android.R.id.text2)

        fun bind(file: File) {
            fileName.text = file.name

            val size = if (file.isDirectory) {
                "${file.listFiles()?.size ?: 0} عناصر"
            } else {
                formatSize(file.length())
            }

            val date = SimpleDateFormat("dd/MM/yyyy", Locale("ar")).format(Date(file.lastModified()))
            fileInfo.text = "$size • $date"

            itemView.setOnClickListener { onFileClick(file) }
        }

        private fun formatSize(bytes: Long): String {
            return when {
                bytes >= 1024 * 1024 -> String.format("%.2f MB", bytes / (1024.0 * 1024.0))
                bytes >= 1024 -> String.format("%.2f KB", bytes / 1024.0)
                else -> "$bytes B"
            }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): FileViewHolder {
        val view = android.widget.TwoLineListItem(parent.context)
        return FileViewHolder(view)
    }

    override fun onBindViewHolder(holder: FileViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class FileDiffCallback : DiffUtil.ItemCallback<File>() {
        override fun areItemsTheSame(oldItem: File, newItem: File) =
            oldItem.absolutePath == newItem.absolutePath

        override fun areContentsTheSame(oldItem: File, newItem: File) =
            oldItem.lastModified() == newItem.lastModified()
    }
}