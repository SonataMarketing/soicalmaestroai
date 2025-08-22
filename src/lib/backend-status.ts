const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export interface BackendStatus {
  isOnline: boolean;
  version?: string;
  bootstrapNeeded?: boolean;
  error?: string;
}

export async function checkBackendStatus(): Promise<BackendStatus> {
  try {
    // Check if backend is online
    const healthResponse = await fetch(`${API_BASE.replace('/api', '')}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!healthResponse.ok) {
      return {
        isOnline: false,
        error: `Backend returned ${healthResponse.status}`
      };
    }

    const healthData = await healthResponse.json();

    // Check bootstrap status
    try {
      const bootstrapResponse = await fetch(`${API_BASE}/auth/bootstrap/status`);
      let bootstrapNeeded = false;

      if (bootstrapResponse.ok) {
        const bootstrapData = await bootstrapResponse.json();
        bootstrapNeeded = bootstrapData.bootstrap_needed || false;
      }

      return {
        isOnline: true,
        version: healthData.version,
        bootstrapNeeded,
      };
    } catch (bootstrapError) {
      // Bootstrap check failed, but backend is online
      return {
        isOnline: true,
        version: healthData.version,
        bootstrapNeeded: true, // Assume bootstrap needed if check fails
      };
    }
  } catch (error) {
    return {
      isOnline: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}

export function getSetupInstructions(status: BackendStatus): string[] {
  if (!status.isOnline) {
    return [
      "1. Navigate to: cd ai-social-manager/backend",
      "2. Install dependencies: pip install -r requirements.txt",
      "3. Create .env file: cp .env.example .env",
      "4. Start backend: uvicorn main:app --reload --host 0.0.0.0 --port 8000"
    ];
  }

  if (status.bootstrapNeeded) {
    return [
      "1. Backend is running ✅",
      "2. Create your first admin account",
      "3. Click 'Sign up' to get started",
      "4. Return here to login"
    ];
  }

  return [
    "✅ Backend is running",
    "✅ Admin account exists",
    "Ready to login!"
  ];
}
