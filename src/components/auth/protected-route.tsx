"use client";

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';
import { Loader2 } from 'lucide-react';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string;
  redirectTo?: string;
}

export function ProtectedRoute({
  children,
  requiredRole,
  redirectTo = '/login'
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, user } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!isLoading) {
      if (!isAuthenticated) {
        // Redirect to login with current path as redirect parameter
        const loginUrl = `${redirectTo}?redirect=${encodeURIComponent(pathname)}`;
        router.push(loginUrl);
        return;
      }

      if (requiredRole && user) {
        // Check role hierarchy
        const roleHierarchy = {
          viewer: 1,
          editor: 2,
          manager: 3,
          admin: 4
        };

        const userLevel = roleHierarchy[user.role as keyof typeof roleHierarchy] || 0;
        const requiredLevel = roleHierarchy[requiredRole as keyof typeof roleHierarchy] || 0;

        if (userLevel < requiredLevel) {
          // User doesn't have sufficient privileges
          router.push('/unauthorized');
          return;
        }
      }
    }
  }, [isAuthenticated, isLoading, user, requiredRole, router, pathname, redirectTo]);

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center space-y-4">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-600" />
          <p className="text-gray-600">Verifying authentication...</p>
        </div>
      </div>
    );
  }

  // Don't render children if not authenticated or insufficient role
  if (!isAuthenticated) {
    return null;
  }

  if (requiredRole && user) {
    const roleHierarchy = {
      viewer: 1,
      editor: 2,
      manager: 3,
      admin: 4
    };

    const userLevel = roleHierarchy[user.role as keyof typeof roleHierarchy] || 0;
    const requiredLevel = roleHierarchy[requiredRole as keyof typeof roleHierarchy] || 0;

    if (userLevel < requiredLevel) {
      return null;
    }
  }

  return <>{children}</>;
}
