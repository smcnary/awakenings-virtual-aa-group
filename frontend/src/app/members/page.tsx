'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ProfileForm } from '@/components/Member/ProfileForm';
import { 
  User, 
  Calendar, 
  Users, 
  CheckCircle
} from 'lucide-react';

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
  group_id?: string;
  meeting_id?: string;
  start_date: string;
  end_date?: string;
  is_active: boolean;
  notes?: string;
}

export default function MembersPage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('profile');

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await fetch('/api/members/profile', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Redirect to login
          window.location.href = '/login';
          return;
        }
        throw new Error('Failed to fetch profile');
      }

      const profileData = await response.json();
      setProfile(profileData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleProfileSave = (updatedProfile: UserProfile) => {
    setProfile(updatedProfile);
  };

  const calculateSobrietyDays = (sobrietyDate: string) => {
    const today = new Date();
    const sobriety = new Date(sobrietyDate);
    const diffTime = Math.abs(today.getTime() - sobriety.getTime());
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading your profile...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Alert variant="destructive" className="max-w-md">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Alert>
          <AlertDescription>Profile not found. Please try logging in again.</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">My Profile</h1>
            <p className="mt-2 text-gray-600">
              Manage your account settings and preferences
            </p>
            
            {/* Privacy Notice */}
            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h3 className="text-lg font-semibold text-blue-800 mb-2">Privacy & Security</h3>
              <p className="text-blue-700 text-sm">
                Your privacy is protected. You control what information is shared in our member directory. 
                Only members who have opted-in to the directory are visible to other members. 
                All contact information is kept secure and only shared with your explicit permission.
              </p>
            </div>
          </div>

          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="profile">Profile</TabsTrigger>
              <TabsTrigger value="service">Service</TabsTrigger>
              <TabsTrigger value="attendance">Attendance</TabsTrigger>
              <TabsTrigger value="directory">Directory</TabsTrigger>
            </TabsList>

            <TabsContent value="profile" className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Profile Overview */}
                <div className="lg:col-span-1">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <User className="w-5 h-5 mr-2" />
                        Profile Overview
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <Label className="text-sm font-medium text-gray-600">Name</Label>
                        <p className="text-lg font-semibold">
                          {profile.preferred_name || 'Not set'}
                        </p>
                      </div>

                      <div>
                        <Label className="text-sm font-medium text-gray-600">Member Since</Label>
                        <p className="text-sm">
                          {formatDate(profile.created_at)}
                        </p>
                      </div>

                      <div>
                        <Label className="text-sm font-medium text-gray-600">Role</Label>
                        <Badge variant="secondary" className="capitalize">
                          {profile.role}
                        </Badge>
                      </div>

                      {profile.sobriety_date && (
                        <div>
                          <Label className="text-sm font-medium text-gray-600">Sobriety</Label>
                          <p className="text-sm">
                            {calculateSobrietyDays(profile.sobriety_date)} days
                          </p>
                          <p className="text-xs text-gray-500">
                            Since {formatDate(profile.sobriety_date)}
                          </p>
                        </div>
                      )}

                      <div>
                        <Label className="text-sm font-medium text-gray-600">Last Login</Label>
                        <p className="text-sm">
                          {profile.last_login ? formatDate(profile.last_login) : 'Never'}
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Profile Form */}
                <div className="lg:col-span-2">
                  <ProfileForm 
                    profile={profile} 
                    onSave={handleProfileSave}
                  />
                </div>
              </div>
            </TabsContent>

            <TabsContent value="service" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <CheckCircle className="w-5 h-5 mr-2" />
                    Service Assignments
                  </CardTitle>
                  <CardDescription>
                    Your current and past service positions
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {profile.service_assignments.length > 0 ? (
                    <div className="space-y-4">
                      {profile.service_assignments.map((assignment) => (
                        <div key={assignment.id} className="border rounded-lg p-4">
                          <div className="flex items-center justify-between">
                            <div>
                              <h3 className="font-semibold capitalize">
                                {assignment.position.replace('_', ' ')}
                              </h3>
                              <p className="text-sm text-gray-600">
                                Since {formatDate(assignment.start_date)}
                                {assignment.end_date && ` - ${formatDate(assignment.end_date)}`}
                              </p>
                              {assignment.notes && (
                                <p className="text-sm text-gray-600 mt-1">
                                  {assignment.notes}
                                </p>
                              )}
                            </div>
                            <Badge variant={assignment.is_active ? 'default' : 'secondary'}>
                              {assignment.is_active ? 'Active' : 'Inactive'}
                            </Badge>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-600">
                      <CheckCircle className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                      <p>No service assignments yet</p>
                      <p className="text-sm">Contact a group secretary to get involved in service</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="attendance" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Calendar className="w-5 h-5 mr-2" />
                    Meeting Attendance
                  </CardTitle>
                  <CardDescription>
                    Your meeting attendance history
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-8 text-gray-600">
                    <Calendar className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                    <p>Meeting attendance tracking coming soon</p>
                    <p className="text-sm">This feature will help you track your meeting participation</p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="directory" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Users className="w-5 h-5 mr-2" />
                    Member Directory
                  </CardTitle>
                  <CardDescription>
                    Connect with other members in the community
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-8 text-gray-600">
                    <Users className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                    <p>Member directory coming soon</p>
                    <p className="text-sm">Find and connect with other members in your area</p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
