"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Separator } from "@/components/ui/separator";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/contexts/auth-context";
import { authService } from "@/lib/auth";
import {
  Wand2, Mail, Lock, Eye, EyeOff, AlertCircle, Loader2,
  User, Crown, CheckCircle, Users, Eye as ViewIcon
} from "lucide-react";

export default function SignupPage() {
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [role, setRole] = useState("editor");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [bootstrapNeeded, setBootstrapNeeded] = useState(false);
  const [checkingBootstrap, setCheckingBootstrap] = useState(true);

  const { isAuthenticated, user } = useAuth();
  const router = useRouter();

  // Check if bootstrap is needed
  useEffect(() => {
    const checkBootstrap = async () => {
      try {
        const status = await authService.checkBootstrapStatus();
        setBootstrapNeeded(status.bootstrap_needed);
      } catch (error) {
        console.error('Failed to check bootstrap status:', error);
      } finally {
        setCheckingBootstrap(false);
      }
    };

    checkBootstrap();
  }, []);

  const validateForm = () => {
    if (!email || !fullName || !password || !confirmPassword) {
      setError("All fields are required");
      return false;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return false;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters long");
      return false;
    }

    // Password strength validation
    const hasUpper = /[A-Z]/.test(password);
    const hasLower = /[a-z]/.test(password);
    const hasNumber = /\d/.test(password);
    const hasSpecial = /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password);

    if (!hasUpper || !hasLower || !hasNumber || !hasSpecial) {
      setError("Password must contain uppercase, lowercase, number, and special character");
      return false;
    }

    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    setSuccess("");

    if (!validateForm()) {
      setIsLoading(false);
      return;
    }

    try {
      if (bootstrapNeeded) {
        // Create first admin user
        await authService.bootstrapAdmin({
          email,
          full_name: fullName,
          password,
          confirm_password: confirmPassword,
        });
        setSuccess("Admin account created successfully! You can now sign in.");
        setTimeout(() => {
          router.push("/login");
        }, 2000);
      } else {
        // Regular user creation (requires admin privileges)
        if (!isAuthenticated || !user || !['admin', 'manager'].includes(user.role)) {
          setError("You need admin privileges to create new accounts");
          setIsLoading(false);
          return;
        }

        await authService.signup({
          email,
          full_name: fullName,
          password,
          role,
        });
        setSuccess("User account created successfully!");
        // Reset form
        setEmail("");
        setFullName("");
        setPassword("");
        setConfirmPassword("");
        setRole("editor");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Signup failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  if (checkingBootstrap) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-600" />
          <p className="text-gray-600">Checking system status...</p>
        </div>
      </div>
    );
  }

  const getRoleInfo = (roleValue: string) => {
    const roles = {
      admin: { label: "Admin", icon: Crown, description: "Full system access", color: "bg-red-100 text-red-800" },
      manager: { label: "Manager", icon: Users, description: "Content & user management", color: "bg-blue-100 text-blue-800" },
      editor: { label: "Editor", icon: User, description: "Content creation & editing", color: "bg-green-100 text-green-800" },
      viewer: { label: "Viewer", icon: ViewIcon, description: "Read-only access", color: "bg-gray-100 text-gray-800" },
    };
    return roles[roleValue as keyof typeof roles] || roles.editor;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="flex items-center justify-center space-x-2">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
              <Wand2 className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900">SocialMaestro</h1>
          </div>
          <p className="text-gray-600">
            {bootstrapNeeded ? "Set up your admin account" : "Create a new account"}
          </p>
        </div>

        {/* Bootstrap Notice */}
        {bootstrapNeeded && (
          <Card className="border-blue-200 bg-blue-50/50">
            <CardContent className="pt-4">
              <div className="text-center space-y-2">
                <Crown className="w-6 h-6 text-blue-600 mx-auto" />
                <h3 className="text-sm font-medium text-blue-800">First-Time Setup</h3>
                <p className="text-xs text-blue-700">
                  No users exist yet. You're creating the first admin account.
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Signup Form */}
        <Card className="shadow-lg border-0 bg-white/80 backdrop-blur">
          <CardHeader className="space-y-1">
            <CardTitle className="text-xl text-center">
              {bootstrapNeeded ? "Create Admin Account" : "Create Account"}
            </CardTitle>
            <CardDescription className="text-center">
              {bootstrapNeeded
                ? "Set up the first administrator account"
                : "Add a new user to your organization"
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {success && (
                <Alert className="border-green-200 bg-green-50">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <AlertDescription className="text-green-800">{success}</AlertDescription>
                </Alert>
              )}

              <div className="space-y-2">
                <Label htmlFor="fullName">Full Name</Label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    id="fullName"
                    type="text"
                    placeholder="John Doe"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="pl-10"
                    required
                    disabled={isLoading}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email Address</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="admin@socialmaestro.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="pl-10"
                    required
                    disabled={isLoading}
                  />
                </div>
              </div>

              {!bootstrapNeeded && (
                <div className="space-y-2">
                  <Label htmlFor="role">Role</Label>
                  <Select value={role} onValueChange={setRole} disabled={isLoading}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {(['viewer', 'editor', 'manager', 'admin'] as const).map((roleValue) => {
                        const roleInfo = getRoleInfo(roleValue);
                        const Icon = roleInfo.icon;
                        return (
                          <SelectItem key={roleValue} value={roleValue}>
                            <div className="flex items-center space-x-2">
                              <Icon className="w-4 h-4" />
                              <span>{roleInfo.label}</span>
                              <Badge variant="secondary" className={roleInfo.color}>
                                {roleInfo.description}
                              </Badge>
                            </div>
                          </SelectItem>
                        );
                      })}
                    </SelectContent>
                  </Select>
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Create a strong password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="pl-10 pr-10"
                    required
                    disabled={isLoading}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    disabled={isLoading}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                <p className="text-xs text-gray-500">
                  Must contain uppercase, lowercase, number, and special character
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Confirm Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    id="confirmPassword"
                    type={showConfirmPassword ? "text" : "password"}
                    placeholder="Confirm your password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="pl-10 pr-10"
                    required
                    disabled={isLoading}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    disabled={isLoading}
                  >
                    {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <Button
                type="submit"
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating account...
                  </>
                ) : (
                  bootstrapNeeded ? "Create Admin Account" : "Create Account"
                )}
              </Button>
            </form>

            {!bootstrapNeeded && (
              <div className="mt-6">
                <Separator />
                <div className="mt-6 text-center">
                  <p className="text-sm text-gray-600">
                    Already have an account?{" "}
                    <Link
                      href="/login"
                      className="text-blue-600 hover:text-blue-700 font-medium hover:underline"
                    >
                      Sign in
                    </Link>
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Requirements Notice */}
        {!bootstrapNeeded && !isAuthenticated && (
          <Card className="border-amber-200 bg-amber-50/50">
            <CardContent className="pt-4">
              <div className="text-center space-y-2">
                <AlertCircle className="w-5 h-5 text-amber-600 mx-auto" />
                <h3 className="text-sm font-medium text-amber-800">Admin Required</h3>
                <p className="text-xs text-amber-700">
                  Creating new accounts requires admin privileges.{" "}
                  <Link href="/login" className="underline hover:no-underline">
                    Sign in
                  </Link>{" "}
                  with admin credentials first.
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Footer */}
        <div className="text-center">
          <p className="text-xs text-gray-500">
            © 2024 SocialMaestro. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  );
}
