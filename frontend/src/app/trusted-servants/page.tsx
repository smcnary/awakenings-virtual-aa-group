"use client";

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface TrustedServant {
  id: number;
  name: string;
  position: string;
  email?: string;
  phone?: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

interface ServicePosition {
  value: string;
  label: string;
  description: string;
}

interface ServiceApplication {
  id: string;
  position: string;
  start_date: string;
  end_date?: string;
  is_active: boolean;
  notes?: string;
  created_at: string;
}

export default function TrustedServants() {
  const [servants, setServants] = useState<TrustedServant[]>([]);
  const [positions, setPositions] = useState<ServicePosition[]>([]);
  const [applications, setApplications] = useState<ServiceApplication[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userRole, setUserRole] = useState<string>('');
  const [showApplicationForm, setShowApplicationForm] = useState(false);
  const [selectedPosition, setSelectedPosition] = useState('');
  const [anonymousName, setAnonymousName] = useState('');

  // Check authentication status
  useEffect(() => {
    checkAuthStatus();
    fetchData();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (token) {
        const response = await fetch('/api/auth/me', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        if (response.ok) {
          const user = await response.json();
          setIsAuthenticated(true);
          setUserRole(user.role);
        }
      }
    } catch (error) {
      console.error('Auth check failed:', error);
    }
  };

  const fetchData = async () => {
    try {
      setLoading(true);
      const [servantsRes, positionsRes, applicationsRes] = await Promise.all([
        fetch('/api/trusted-servants/'),
        fetch('/api/trusted-servants/positions'),
        isAuthenticated ? fetch('/api/trusted-servants/my-applications', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }) : Promise.resolve(null)
      ]);

      if (servantsRes.ok) {
        const servantsData = await servantsRes.json();
        setServants(servantsData);
      }

      if (positionsRes.ok) {
        const positionsData = await positionsRes.json();
        setPositions(positionsData);
      }

      if (applicationsRes?.ok) {
        const applicationsData = await applicationsRes.json();
        setApplications(applicationsData);
      }
    } catch (error) {
      setError('Failed to load data');
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const createAnonymousAccount = async () => {
    try {
      const response = await fetch('/api/auth/anonymous', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        setIsAuthenticated(true);
        setUserRole(data.user.role);
        setSuccess('Anonymous account created successfully! You can now apply for service positions.');
        await fetchData(); // Refresh data to show applications
      } else {
        setError('Failed to create anonymous account');
      }
    } catch (error) {
      setError('Failed to create anonymous account');
      console.error('Error creating anonymous account:', error);
    }
  };

  const applyForPosition = async () => {
    if (!selectedPosition) {
      setError('Please select a position');
      return;
    }

    try {
      const response = await fetch('/api/trusted-servants/apply', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          position: selectedPosition,
          anonymous_name: anonymousName || undefined
        })
      });

      if (response.ok) {
        setSuccess('Application submitted successfully!');
        setShowApplicationForm(false);
        setSelectedPosition('');
        setAnonymousName('');
        await fetchData(); // Refresh applications
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to submit application');
      }
    } catch (error) {
      setError('Failed to submit application');
      console.error('Error submitting application:', error);
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setIsAuthenticated(false);
    setUserRole('');
    setApplications([]);
    setSuccess('Logged out successfully');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading trusted servants...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Hero Section */}
      <section className="bg-white rounded-lg shadow-lg p-8 mb-8 text-center">
        <h2 className="text-3xl font-bold text-slate-800 mb-4">Trusted Servants</h2>
        <p className="text-lg text-gray-600">The members who serve our group in various capacities</p>
        
        {/* Payment Links */}
        <div className="mt-6 space-y-4">
          <h3 className="text-xl font-semibold text-slate-800 mb-3">Contribute to Our Group</h3>
          <p className="text-gray-600 mb-4">Service work contributions to Central Service Office, District, Area, and GSO</p>
          <div className="flex justify-center gap-4 flex-wrap">
            <a 
              href="#" 
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors inline-flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M19.54 8.46l-1.42-1.42L16.8 9.2c-.39-.39-1.01-.39-1.4 0s-.39 1.01 0 1.4l1.32 1.32c-.39.39-.39 1.01 0 1.4s1.01.39 1.4 0l1.32-1.32c.39.39 1.01.39 1.4 0s.39-1.01 0-1.4l-1.32-1.32zM12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
              </svg>
              Venmo
            </a>
            <a 
              href="#" 
              className="bg-yellow-500 text-white px-6 py-3 rounded-lg font-medium hover:bg-yellow-600 transition-colors inline-flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M7.076 21.337H2.47a.641.641 0 0 1-.633-.74L4.944.901C5.026.382 5.474 0 5.998 0h7.46c2.57 0 4.578.543 5.69 1.81 1.01 1.15 1.304 2.42 1.012 4.287-.023.143-.047.288-.077.437-.983 5.05-4.349 6.797-8.647 6.797h-2.19c-.524 0-.968.382-1.05.9l-1.12 7.106zm14.146-14.42a3.35 3.35 0 0 1-.443-.272c-.605-.4-1.348-.627-2.076-.627H12.77c-.524 0-.968.382-1.05.9L10.6 16.4h2.19c.524 0 .968-.382 1.05-.9l1.12-7.106h2.19c2.57 0 4.578-.543 5.69-1.81.906-1.036 1.19-2.178.91-3.716-.023-.143-.047-.288-.077-.437z"/>
              </svg>
              PayPal
            </a>
          </div>
          <p className="text-sm text-gray-500 mt-3">Donations will be made to Central Service, District, Area and GSO</p>
        </div>
        
        {/* Authentication Status */}
        <div className="mt-6">
          {isAuthenticated ? (
            <div className="flex items-center justify-center gap-4">
              <Badge variant="outline" className="text-green-600 border-green-600">
                Authenticated as {userRole}
              </Badge>
              <Button onClick={logout} variant="outline" size="sm">
                Logout
              </Button>
            </div>
          ) : (
            <Button onClick={createAnonymousAccount} className="bg-blue-600 hover:bg-blue-700">
              Create Anonymous Account
            </Button>
          )}
        </div>
      </section>

      {/* Alerts */}
      {error && (
        <Alert className="mb-6 border-red-200 bg-red-50">
          <AlertDescription className="text-red-800">{error}</AlertDescription>
        </Alert>
      )}
      
      {success && (
        <Alert className="mb-6 border-green-200 bg-green-50">
          <AlertDescription className="text-green-800">{success}</AlertDescription>
        </Alert>
      )}

      {/* Main Content */}
      <Tabs defaultValue="servants" className="space-y-8">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="servants">Current Servants</TabsTrigger>
          <TabsTrigger value="positions">Service Positions</TabsTrigger>
          <TabsTrigger value="applications">My Applications</TabsTrigger>
        </TabsList>

        <TabsContent value="servants" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Current Trusted Servants</CardTitle>
            </CardHeader>
            <CardContent>
              {servants.length === 0 ? (
                <p className="text-gray-600 text-center py-8">
                  No trusted servants currently assigned. Positions are open for service!
                </p>
              ) : (
                <div className="grid gap-4">
                  {servants.map((servant) => (
                    <Card key={servant.id} className="border-l-4 border-blue-500">
                      <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="text-xl font-semibold text-slate-800">
                              {servant.name}
                            </h4>
                            <p className="text-lg text-blue-600 font-medium">
                              {servant.position.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </p>
                            {servant.description && (
                              <p className="text-gray-600 mt-2">{servant.description}</p>
                            )}
                          </div>
                          <Badge variant="outline" className="text-green-600 border-green-600">
                            Active
                          </Badge>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="positions" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Available Service Positions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4">
                {positions.map((position) => (
                  <Card key={position.value} className="border-l-4 border-green-500">
                    <CardContent className="pt-6">
                      <h4 className="text-xl font-semibold text-slate-800 mb-2">
                        {position.label}
                      </h4>
                      <p className="text-gray-600 mb-4">{position.description}</p>
                      {isAuthenticated && (
                        <Button 
                          onClick={() => {
                            setSelectedPosition(position.value);
                            setShowApplicationForm(true);
                          }}
                          size="sm"
                          className="bg-green-600 hover:bg-green-700"
                        >
                          Apply for Position
                        </Button>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="applications" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>My Service Applications</CardTitle>
            </CardHeader>
            <CardContent>
              {!isAuthenticated ? (
                <div className="text-center py-8">
                  <p className="text-gray-600 mb-4">
                    Create an anonymous account to apply for service positions.
                  </p>
                  <Button onClick={createAnonymousAccount} className="bg-blue-600 hover:bg-blue-700">
                    Create Anonymous Account
                  </Button>
                </div>
              ) : applications.length === 0 ? (
                <p className="text-gray-600 text-center py-8">
                  You haven&apos;t applied for any service positions yet.
                </p>
              ) : (
                <div className="grid gap-4">
                  {applications.map((application) => (
                    <Card key={application.id} className="border-l-4 border-purple-500">
                      <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="text-xl font-semibold text-slate-800">
                              {application.position.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </h4>
                            <p className="text-gray-600">
                              Applied on {new Date(application.created_at).toLocaleDateString()}
                            </p>
                            {application.notes && (
                              <p className="text-gray-600 mt-2">{application.notes}</p>
                            )}
                          </div>
                          <Badge 
                            variant="outline" 
                            className={application.is_active ? "text-green-600 border-green-600" : "text-gray-600 border-gray-600"}
                          >
                            {application.is_active ? 'Active' : 'Inactive'}
                          </Badge>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Application Form Modal */}
      {showApplicationForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Apply for Service Position</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="position">Position</Label>
                <Select value={selectedPosition} onValueChange={setSelectedPosition}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a position" />
                  </SelectTrigger>
                  <SelectContent>
                    {positions.map((position) => (
                      <SelectItem key={position.value} value={position.value}>
                        {position.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label htmlFor="anonymousName">Anonymous Name (Optional)</Label>
                <Input
                  id="anonymousName"
                  value={anonymousName}
                  onChange={(e) => setAnonymousName(e.target.value)}
                  placeholder="Enter a name to use for this application"
                />
                <p className="text-sm text-gray-600 mt-1">
                  This name will be used in the application but won&apos;t be linked to your account.
                </p>
              </div>

              <div className="flex gap-2 pt-4">
                <Button onClick={applyForPosition} className="flex-1 bg-blue-600 hover:bg-blue-700">
                  Submit Application
                </Button>
                <Button 
                  onClick={() => setShowApplicationForm(false)} 
                  variant="outline" 
                  className="flex-1"
                >
                  Cancel
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
