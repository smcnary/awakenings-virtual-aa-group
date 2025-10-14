'use client';

import { MagicLinkLogin } from '@/components/Auth/MagicLinkLogin';

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">AA Virtual</h1>
          <p className="mt-2 text-gray-600">
            Sign in to access your account and connect with your recovery community
          </p>
        </div>
        
        <MagicLinkLogin 
          onSuccess={() => {
            // Redirect to dashboard or intended page
            window.location.href = '/dashboard';
          }}
        />
        
        <div className="text-center text-sm text-gray-600">
          <p>
            New to AA Virtual? You'll create an account when you sign in for the first time.
          </p>
        </div>
      </div>
    </div>
  );
}
