'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Save, Globe, Bell } from 'lucide-react';
import { toast } from 'sonner';

interface UserProfile {
  id: string;
  preferred_name?: string;
  sobriety_date?: string;
  timezone: string;
  language: string;
  show_sobriety_date: boolean;
  show_in_directory: boolean;
  allow_contact: boolean;
  role: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
  service_assignments: ServiceAssignment[];
  notification_preferences: {
    email_notifications: boolean;
    meeting_reminders: boolean;
    service_updates: boolean;
    marketing: boolean;
  };
}

interface ServiceAssignment {
  id: string;
  position: string;
  is_active: boolean;
  start_date: string;
  end_date?: string;
  notes?: string;
}

interface ProfileFormProps {
  profile?: UserProfile;
  onSave?: (profile: UserProfile) => void;
}

export function ProfileForm({ profile, onSave }: ProfileFormProps) {
  const [formData, setFormData] = useState<UserProfile>({
    id: '',
    timezone: 'America/Chicago',
    language: 'en',
    show_sobriety_date: false,
    show_in_directory: true,
    allow_contact: false,
    role: 'guest',
    is_active: true,
    created_at: '',
    service_assignments: [],
    notification_preferences: {
      email_notifications: true,
      meeting_reminders: true,
      service_updates: false,
      marketing: false,
    },
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (profile) {
      setFormData(profile);
    }
  }, [profile]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('/api/members/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update profile');
      }

      const updatedProfile = await response.json();
      toast.success('Profile updated successfully');
      onSave?.(updatedProfile);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (field: string, value: unknown) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleNotificationChange = (key: string, value: boolean) => {
    setFormData(prev => ({
      ...prev,
      notification_preferences: {
        ...prev.notification_preferences,
        [key]: value,
      },
    }));
  };

  const timezones = [
    { value: 'America/New_York', label: 'Eastern Time' },
    { value: 'America/Chicago', label: 'Central Time' },
    { value: 'America/Denver', label: 'Mountain Time' },
    { value: 'America/Los_Angeles', label: 'Pacific Time' },
    { value: 'America/Anchorage', label: 'Alaska Time' },
    { value: 'Pacific/Honolulu', label: 'Hawaii Time' },
  ];

  const languages = [
    { value: 'en', label: 'English' },
    { value: 'es', label: 'Español' },
    { value: 'fr', label: 'Français' },
  ];

  return (
    <div className="space-y-6">
      {/* Basic Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Globe className="w-5 h-5 mr-2" />
            Basic Information
          </CardTitle>
          <CardDescription>
            Update your basic profile information
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="preferred_name">Preferred Name</Label>
              <Input
                id="preferred_name"
                value={formData.preferred_name || ''}
                onChange={(e) => handleInputChange('preferred_name', e.target.value)}
                placeholder="How would you like to be called?"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="sobriety_date">Sobriety Date</Label>
              <Input
                id="sobriety_date"
                type="date"
                value={formData.sobriety_date || ''}
                onChange={(e) => handleInputChange('sobriety_date', e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="timezone">Timezone</Label>
              <Select
                value={formData.timezone}
                onValueChange={(value) => handleInputChange('timezone', value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {timezones.map((tz) => (
                    <SelectItem key={tz.value} value={tz.value}>
                      {tz.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="language">Language</Label>
              <Select
                value={formData.language}
                onValueChange={(value) => handleInputChange('language', value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {languages.map((lang) => (
                    <SelectItem key={lang.value} value={lang.value}>
                      {lang.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Privacy Settings */}
      <Card>
        <CardHeader>
          <CardTitle>Privacy Settings</CardTitle>
          <CardDescription>
            Control what information is visible to others
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Show Sobriety Date</Label>
              <p className="text-sm text-gray-600">
                Allow others to see your sobriety date
              </p>
            </div>
            <Switch
              checked={formData.show_sobriety_date}
              onCheckedChange={(checked) => handleInputChange('show_sobriety_date', checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Show in Directory</Label>
              <p className="text-sm text-gray-600">
                Include your profile in the member directory
              </p>
            </div>
            <Switch
              checked={formData.show_in_directory}
              onCheckedChange={(checked) => handleInputChange('show_in_directory', checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Allow Contact</Label>
              <p className="text-sm text-gray-600">
                Let other members contact you directly
              </p>
            </div>
            <Switch
              checked={formData.allow_contact}
              onCheckedChange={(checked) => handleInputChange('allow_contact', checked)}
            />
          </div>
        </CardContent>
      </Card>

      {/* Notification Preferences */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Bell className="w-5 h-5 mr-2" />
            Notification Preferences
          </CardTitle>
          <CardDescription>
            Choose how you&apos;d like to be notified
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Email Notifications</Label>
              <p className="text-sm text-gray-600">
                Receive important updates via email
              </p>
            </div>
            <Switch
              checked={formData.notification_preferences.email_notifications}
              onCheckedChange={(checked) => handleNotificationChange('email_notifications', checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Meeting Reminders</Label>
              <p className="text-sm text-gray-600">
                Get reminders about upcoming meetings
              </p>
            </div>
            <Switch
              checked={formData.notification_preferences.meeting_reminders}
              onCheckedChange={(checked) => handleNotificationChange('meeting_reminders', checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Service Updates</Label>
              <p className="text-sm text-gray-600">
                Notifications about service opportunities
              </p>
            </div>
            <Switch
              checked={formData.notification_preferences.service_updates}
              onCheckedChange={(checked) => handleNotificationChange('service_updates', checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Marketing</Label>
              <p className="text-sm text-gray-600">
                Receive updates about new features and events
              </p>
            </div>
            <Switch
              checked={formData.notification_preferences.marketing}
              onCheckedChange={(checked) => handleNotificationChange('marketing', checked)}
            />
          </div>
        </CardContent>
      </Card>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="flex justify-end">
        <Button 
          onClick={handleSubmit} 
          disabled={isLoading}
          className="min-w-32"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <Save className="w-4 h-4 mr-2" />
              Save Changes
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
