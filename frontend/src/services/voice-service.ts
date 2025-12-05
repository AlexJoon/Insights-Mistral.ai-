/**
 * Voice Transcription Service
 * Handles communication with backend voice transcription API
 *
 * Design Pattern: Service Layer Pattern
 * Purpose: Abstract voice API calls from components
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface TranscriptionResponse {
  text: string;
  language?: string;
  duration?: number;
}

export interface TranscriptionError {
  error: string;
  details?: string;
}

class VoiceService {
  /**
   * Transcribe audio blob to text using Voxtral API
   *
   * @param audioBlob - Audio file blob (webm, mp3, wav, etc.)
   * @returns Transcribed text
   */
  async transcribeAudio(audioBlob: Blob): Promise<string> {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');

    try {
      const response = await fetch(`${API_BASE_URL}/api/voice/transcribe`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData: TranscriptionError = await response.json().catch(() => ({
          error: 'Failed to transcribe audio'
        }));
        throw new Error(errorData.error || 'Transcription failed');
      }

      const data: TranscriptionResponse = await response.json();

      if (!data.text) {
        throw new Error('No transcription text received');
      }

      return data.text;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Unknown error during transcription');
    }
  }

  /**
   * Check if voice transcription is available
   *
   * @returns True if voice API is available
   */
  async checkAvailability(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }
}

// Export singleton instance
export const voiceService = new VoiceService();
