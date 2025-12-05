/**
 * File Upload Service
 * Handles file upload operations to the backend API
 *
 * Design Pattern: Service Layer Pattern
 * Purpose: Encapsulate file upload logic and API communication
 */

import { FileUploadResponse, FileMetadata } from '@/types/api';

export class FileUploadService {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  /**
   * Upload a file to the backend for RAG ingestion and chat context
   *
   * @param file - File to upload
   * @param conversationId - Optional conversation ID to associate file with
   * @returns Upload response with file metadata
   */
  async uploadFile(
    file: File,
    conversationId?: string
  ): Promise<FileUploadResponse> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      if (conversationId) {
        formData.append('conversation_id', conversationId);
      }

      const response = await fetch(`${this.baseUrl}/api/files/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `Upload failed: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('File upload error:', error);
      throw error;
    }
  }

  /**
   * Get metadata for uploaded files in a conversation
   *
   * @param conversationId - Conversation ID
   * @returns Array of file metadata
   */
  async getConversationFiles(
    conversationId: string
  ): Promise<FileMetadata[]> {
    try {
      const response = await fetch(
        `${this.baseUrl}/api/files/conversation/${conversationId}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch files: ${response.statusText}`);
      }

      const data = await response.json();
      return data.files || [];
    } catch (error) {
      console.error('Error fetching conversation files:', error);
      return [];
    }
  }

  /**
   * Delete an uploaded file
   *
   * @param fileId - File ID to delete
   * @returns Success status
   */
  async deleteFile(fileId: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/files/${fileId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to delete file: ${response.statusText}`);
      }

      return true;
    } catch (error) {
      console.error('Error deleting file:', error);
      return false;
    }
  }

  /**
   * Validate file before upload
   *
   * @param file - File to validate
   * @param maxSizeMB - Maximum file size in MB
   * @param allowedTypes - Allowed file extensions
   * @returns Validation result
   */
  validateFile(
    file: File,
    maxSizeMB: number = 10,
    allowedTypes: string[] = ['.pdf', '.docx', '.txt', '.md']
  ): { valid: boolean; error?: string } {
    // Check file size
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxSizeBytes) {
      return {
        valid: false,
        error: `File size must be less than ${maxSizeMB}MB`,
      };
    }

    // Check file type
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!allowedTypes.includes(fileExtension)) {
      return {
        valid: false,
        error: `File type not supported. Accepted: ${allowedTypes.join(', ')}`,
      };
    }

    return { valid: true };
  }
}

// Export singleton instance
export const fileUploadService = new FileUploadService();
