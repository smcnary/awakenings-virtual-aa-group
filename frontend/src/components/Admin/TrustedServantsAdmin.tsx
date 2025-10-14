"use client";

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
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
  user_id: string;
}

export default function TrustedServantsAdmin() {
  const [servants, setServants] = useState<TrustedServant[]>([]);
  const [positions, setPositions] = useState<ServicePosition[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);
  const [editingServant, setEditingServant] = useState<TrustedServant | null>(null);
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    position: '',
    email: '',
    phone: '',
    description: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      
      const [servantsRes, positionsRes] = await Promise.all([
        fetch('/api/trusted-servants/', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }),
        fetch('/api/trusted-servants/positions', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
      ]);

      if (servantsRes.ok) {
        const servantsData = await servantsRes.json();
        setServants(servantsData);
      }

      if (positionsRes.ok) {
        const positionsData = await positionsRes.json();
        setPositions(positionsData);
      }
    } catch (error) {
      setError('Failed to load data');
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateServant = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/trusted-servants/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        setSuccess('Trusted servant created successfully!');
        setShowCreateForm(false);
        resetForm();
        await fetchData();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create trusted servant');
      }
    } catch (error) {
      setError('Failed to create trusted servant');
      console.error('Error creating trusted servant:', error);
    }
  };

  const handleEditServant = async () => {
    if (!editingServant) return;

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/trusted-servants/${editingServant.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        setSuccess('Trusted servant updated successfully!');
        setShowEditForm(false);
        setEditingServant(null);
        resetForm();
        await fetchData();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to update trusted servant');
      }
    } catch (error) {
      setError('Failed to update trusted servant');
      console.error('Error updating trusted servant:', error);
    }
  };

  const handleDeleteServant = async (servantId: number) => {
    if (!confirm('Are you sure you want to remove this trusted servant?')) return;

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/trusted-servants/${servantId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setSuccess('Trusted servant removed successfully!');
        await fetchData();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to remove trusted servant');
      }
    } catch (error) {
      setError('Failed to remove trusted servant');
      console.error('Error removing trusted servant:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      position: '',
      email: '',
      phone: '',
      description: ''
    });
  };

  const openEditForm = (servant: TrustedServant) => {
    setEditingServant(servant);
    setFormData({
      name: servant.name,
      position: servant.position,
      email: servant.email || '',
      phone: servant.phone || '',
      description: servant.description || ''
    });
    setShowEditForm(true);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading admin panel...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-slate-800">Trusted Servants Admin</h1>
        <Button 
          onClick={() => setShowCreateForm(true)}
          className="bg-blue-600 hover:bg-blue-700"
        >
          Add Trusted Servant
        </Button>
      </div>

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

      {/* Current Trusted Servants */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Current Trusted Servants</CardTitle>
        </CardHeader>
        <CardContent>
          {servants.length === 0 ? (
            <p className="text-gray-600 text-center py-8">
              No trusted servants currently assigned.
            </p>
          ) : (
            <div className="grid gap-4">
              {servants.map((servant) => (
                <Card key={servant.id} className="border-l-4 border-blue-500">
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h4 className="text-xl font-semibold text-slate-800">
                          {servant.name}
                        </h4>
                        <p className="text-lg text-blue-600 font-medium">
                          {servant.position.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </p>
                        {servant.email && (
                          <p className="text-gray-600">Email: {servant.email}</p>
                        )}
                        {servant.phone && (
                          <p className="text-gray-600">Phone: {servant.phone}</p>
                        )}
                        {servant.description && (
                          <p className="text-gray-600 mt-2">{servant.description}</p>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-green-600 border-green-600">
                          Active
                        </Badge>
                        <Button 
                          onClick={() => openEditForm(servant)}
                          variant="outline"
                          size="sm"
                        >
                          Edit
                        </Button>
                        <Button 
                          onClick={() => handleDeleteServant(servant.id)}
                          variant="outline"
                          size="sm"
                          className="text-red-600 hover:text-red-700"
                        >
                          Remove
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Available Positions */}
      <Card>
        <CardHeader>
          <CardTitle>Available Service Positions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4">
            {positions.map((position) => {
              const isFilled = servants.some(s => s.position === position.value);
              return (
                <Card key={position.value} className={`border-l-4 ${isFilled ? 'border-gray-300' : 'border-green-500'}`}>
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="text-xl font-semibold text-slate-800">
                          {position.label}
                        </h4>
                        <p className="text-gray-600">{position.description}</p>
                      </div>
                      <Badge 
                        variant="outline" 
                        className={isFilled ? "text-gray-600 border-gray-600" : "text-green-600 border-green-600"}
                      >
                        {isFilled ? 'Filled' : 'Open'}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Create Form Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Add Trusted Servant</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="name">Name</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({...formData, name: e.target.value})}
                  placeholder="Enter servant's name"
                />
              </div>
              
              <div>
                <Label htmlFor="position">Position</Label>
                <Select value={formData.position} onValueChange={(value) => setFormData({...formData, position: value})}>
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
                <Label htmlFor="email">Email (Optional)</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({...formData, email: e.target.value})}
                  placeholder="Enter email address"
                />
              </div>

              <div>
                <Label htmlFor="phone">Phone (Optional)</Label>
                <Input
                  id="phone"
                  value={formData.phone}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({...formData, phone: e.target.value})}
                  placeholder="Enter phone number"
                />
              </div>

              <div>
                <Label htmlFor="description">Description (Optional)</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setFormData({...formData, description: e.target.value})}
                  placeholder="Enter description of responsibilities"
                  rows={3}
                />
              </div>

              <div className="flex gap-2 pt-4">
                <Button onClick={handleCreateServant} className="flex-1 bg-blue-600 hover:bg-blue-700">
                  Create
                </Button>
                <Button 
                  onClick={() => {
                    setShowCreateForm(false);
                    resetForm();
                  }} 
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

      {/* Edit Form Modal */}
      {showEditForm && editingServant && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Edit Trusted Servant</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="edit-name">Name</Label>
                <Input
                  id="edit-name"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  placeholder="Enter servant's name"
                />
              </div>
              
              <div>
                <Label htmlFor="edit-position">Position</Label>
                <Select value={formData.position} onValueChange={(value) => setFormData({...formData, position: value})}>
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
                <Label htmlFor="edit-email">Email (Optional)</Label>
                <Input
                  id="edit-email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  placeholder="Enter email address"
                />
              </div>

              <div>
                <Label htmlFor="edit-phone">Phone (Optional)</Label>
                <Input
                  id="edit-phone"
                  value={formData.phone}
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                  placeholder="Enter phone number"
                />
              </div>

              <div>
                <Label htmlFor="edit-description">Description (Optional)</Label>
                <Textarea
                  id="edit-description"
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  placeholder="Enter description of responsibilities"
                  rows={3}
                />
              </div>

              <div className="flex gap-2 pt-4">
                <Button onClick={handleEditServant} className="flex-1 bg-blue-600 hover:bg-blue-700">
                  Update
                </Button>
                <Button 
                  onClick={() => {
                    setShowEditForm(false);
                    setEditingServant(null);
                    resetForm();
                  }} 
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
