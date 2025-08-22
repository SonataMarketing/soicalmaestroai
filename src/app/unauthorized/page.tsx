"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/contexts/auth-context";
import { Shield, ArrowLeft, Home, LogOut } from "lucide-react";

export default function UnauthorizedPage() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-orange-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        {/* Icon and Title */}
        <div className="text-center space-y-4">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto">
            <Shield className="w-8 h-8 text-red-600" />
          </div>
          <div className="space-y-2">
            <h1 className="text-2xl font-bold text-gray-900">Access Denied</h1>
            <p className="text-gray-600">You don't have permission to access this resource</p>
          </div>
        </div>

        {/* Error Details */}
        <Card className="shadow-lg border-0 bg-white/80 backdrop-blur">
          <CardHeader className="text-center">
            <CardTitle className="text-lg text-red-700">Insufficient Privileges</CardTitle>
            <CardDescription>
              Your current role doesn't allow access to this feature
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {user && (
              <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                <div className="text-sm">
                  <span className="text-gray-600">Signed in as:</span>
                  <span className="ml-2 font-medium">{user.full_name}</span>
                </div>
                <div className="text-sm">
                  <span className="text-gray-600">Role:</span>
                  <span className="ml-2 font-medium capitalize">{user.role}</span>
                </div>
                <div className="text-sm">
                  <span className="text-gray-600">Email:</span>
                  <span className="ml-2 font-medium">{user.email}</span>
                </div>
              </div>
            )}

            <div className="text-sm text-gray-600 space-y-2">
              <p>To access this feature, you need:</p>
              <ul className="list-disc list-inside space-y-1 ml-4">
                <li>Higher-level permissions from your administrator</li>
                <li>Or contact your system administrator for access</li>
              </ul>
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="space-y-3">
          <Link href="/" className="block">
            <Button className="w-full" variant="default">
              <Home className="w-4 h-4 mr-2" />
              Return to Dashboard
            </Button>
          </Link>

          <Button
            variant="outline"
            className="w-full"
            onClick={() => window.history.back()}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Go Back
          </Button>

          <Button
            variant="ghost"
            className="w-full text-red-600 hover:text-red-700 hover:bg-red-50"
            onClick={logout}
          >
            <LogOut className="w-4 h-4 mr-2" />
            Sign Out
          </Button>
        </div>

        {/* Help */}
        <Card className="border-blue-200 bg-blue-50/50">
          <CardContent className="pt-4">
            <div className="text-center space-y-2">
              <h3 className="text-sm font-medium text-blue-800">Need Help?</h3>
              <p className="text-xs text-blue-700">
                Contact your administrator at{" "}
                <a
                  href="mailto:admin@socialmaestro.com"
                  className="underline hover:no-underline"
                >
                  admin@socialmaestro.com
                </a>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
