'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Mail, Phone, CheckCircle } from 'lucide-react';

interface MagicLinkLoginProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

export function MagicLinkLogin({ onSuccess, onCancel }: MagicLinkLoginProps) {
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSent, setIsSent] = useState(false);
  const [error, setError] = useState('');
  const [contactMethod, setContactMethod] = useState<'email' | 'phone'>('email');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('/api/auth/magic-link', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          [contactMethod]: contactMethod === 'email' ? email : phone,
          purpose: 'login'
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to send magic link');
      }

      setIsSent(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleMagicLinkVerification = async (token: string) => {
    try {
      const response = await fetch('/api/auth/verify-magic-link', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token }),
      });

      if (!response.ok) {
        throw new Error('Invalid or expired magic link');
      }

      const data = await response.json();
      
      // Store tokens
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      
      onSuccess?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Verification failed');
    }
  };

  // Check for magic link token in URL
  React.useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    
    if (token) {
      handleMagicLinkVerification(token);
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  if (isSent) {
    return (
      <Card className="w-full max-w-md mx-auto">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
            <CheckCircle className="w-6 h-6 text-green-600" />
          </div>
          <CardTitle>Check Your {contactMethod === 'email' ? 'Email' : 'Phone'}</CardTitle>
          <CardDescription>
            We've sent you a magic link to sign in. Click the link to continue.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Alert>
            <AlertDescription>
              The link will expire in 15 minutes for your security.
            </AlertDescription>
          </Alert>
          <Button 
            variant="outline" 
            onClick={() => setIsSent(false)}
            className="w-full"
          >
            Try Different {contactMethod === 'email' ? 'Email' : 'Phone'}
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle className="text-center">Sign In to AA Virtual</CardTitle>
        <CardDescription className="text-center">
          We'll send you a secure link to sign in without a password
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Contact Method Toggle */}
          <div className="flex space-x-2">
            <Button
              type="button"
              variant={contactMethod === 'email' ? 'default' : 'outline'}
              onClick={() => setContactMethod('email')}
              className="flex-1"
            >
              <Mail className="w-4 h-4 mr-2" />
              Email
            </Button>
            <Button
              type="button"
              variant={contactMethod === 'phone' ? 'default' : 'outline'}
              onClick={() => setContactMethod('phone')}
              className="flex-1"
            >
              <Phone className="w-4 h-4 mr-2" />
              Phone
            </Button>
          </div>

          {/* Contact Input */}
          {contactMethod === 'email' ? (
            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                required
              />
            </div>
          ) : (
            <div className="space-y-2">
              <Label htmlFor="phone">Phone Number</Label>
              <Input
                id="phone"
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+1 (555) 123-4567"
                required
              />
            </div>
          )}

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Sending Link...
              </>
            ) : (
              'Send Magic Link'
            )}
          </Button>
        </form>

        <div className="mt-6 text-center text-sm text-gray-600">
          <p>
            By signing in, you agree to our{' '}
            <a href="/privacy" className="text-blue-600 hover:underline">
              Privacy Policy
            </a>{' '}
            and{' '}
            <a href="/terms" className="text-blue-600 hover:underline">
              Terms of Service
            </a>
          </p>
        </div>

        {onCancel && (
          <Button 
            variant="ghost" 
            onClick={onCancel}
            className="w-full mt-4"
          >
            Cancel
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
