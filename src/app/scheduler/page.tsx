"use client";

import { useState } from "react";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Calendar } from "@/components/ui/calendar";
import {
  Calendar as CalendarIcon,
  Clock,
  Image,
  Video,
  Instagram,
  Twitter,
  Facebook,
  Linkedin,
  Play,
  Pause,
  Settings,
  Plus,
  Edit,
  Trash2,
  BarChart3,
  ChevronLeft,
  ChevronRight
} from "lucide-react";
import { format, addDays, isSameDay } from "date-fns";

const scheduledPosts = [
  {
    id: 1,
    date: new Date(2024, 7, 22, 9, 0), // Aug 22, 9:00 AM
    platform: "Instagram",
    type: "photo",
    content: "🌟 Start your Thursday with some inspiration! Our AI tools are helping businesses create content that truly connects with their audience...",
    imageUrl: "https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=300&h=300&fit=crop",
    status: "scheduled",
    engagement: { estimated: "High" }
  },
  {
    id: 2,
    date: new Date(2024, 7, 22, 17, 0), // Aug 22, 5:00 PM
    platform: "Instagram",
    type: "video",
    content: "💡 Behind the scenes: How our AI analyzes thousands of posts to understand what content performs best for your brand...",
    thumbnailUrl: "https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=300&h=300&fit=crop",
    status: "scheduled",
    engagement: { estimated: "Medium" }
  },
  {
    id: 3,
    date: new Date(2024, 7, 23, 10, 0), // Aug 23, 10:00 AM
    platform: "LinkedIn",
    type: "photo",
    content: "The future of content marketing is intelligent automation. Companies using AI-driven strategies are seeing remarkable results...",
    imageUrl: "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=300&h=300&fit=crop",
    status: "scheduled",
    engagement: { estimated: "High" }
  },
  {
    id: 4,
    date: new Date(2024, 7, 23, 16, 30), // Aug 23, 4:30 PM
    platform: "Twitter",
    type: "video",
    content: "Quick tip: The best performing content alternates between educational and entertaining. Here's how to find that balance...",
    thumbnailUrl: "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=300&h=300&fit=crop",
    status: "scheduled",
    engagement: { estimated: "Medium" }
  }
];

const automationSettings = {
  enabled: true,
  timesPerDay: 2,
  firstPost: "09:00",
  secondPost: "17:00",
  alternateContent: true,
  platforms: ["instagram", "linkedin", "twitter"],
  weekendPosting: false
};

const timeSlots = [
  "06:00", "07:00", "08:00", "09:00", "10:00", "11:00",
  "12:00", "13:00", "14:00", "15:00", "16:00", "17:00",
  "18:00", "19:00", "20:00", "21:00", "22:00"
];

export default function ContentScheduler() {
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [viewMode, setViewMode] = useState<"calendar" | "list">("calendar");
  const [autoSettings, setAutoSettings] = useState(automationSettings);

  const getPostsForDate = (date: Date) => {
    return scheduledPosts.filter(post => isSameDay(post.date, date));
  };

  const getPlatformIcon = (platform: string) => {
    switch (platform.toLowerCase()) {
      case "instagram":
        return <Instagram className="h-4 w-4 text-pink-500" />;
      case "twitter":
        return <Twitter className="h-4 w-4 text-blue-500" />;
      case "linkedin":
        return <Linkedin className="h-4 w-4 text-blue-600" />;
      case "facebook":
        return <Facebook className="h-4 w-4 text-blue-700" />;
      default:
        return <Instagram className="h-4 w-4" />;
    }
  };

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Content Scheduler</h1>
            <p className="text-gray-600">Automate your posting schedule with intelligent timing</p>
          </div>
          <div className="flex space-x-3">
            <Button variant="outline">
              <Settings className="h-4 w-4 mr-2" />
              Automation Settings
            </Button>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Schedule Post
            </Button>
          </div>
        </div>

        {/* Automation Status */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Automation Status</span>
              <Switch
                checked={autoSettings.enabled}
                onCheckedChange={(checked) => setAutoSettings({...autoSettings, enabled: checked})}
              />
            </CardTitle>
            <CardDescription>
              {autoSettings.enabled
                ? `Posting ${autoSettings.timesPerDay} times daily at ${autoSettings.firstPost} and ${autoSettings.secondPost}`
                : "Automation is currently disabled"
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="flex items-center space-x-2">
                <Clock className="h-4 w-4 text-gray-500" />
                <span className="text-sm">
                  Next post: Today at {autoSettings.firstPost}
                </span>
              </div>
              <div className="flex items-center space-x-2">
                {autoSettings.alternateContent ? (
                  <>
                    <Image className="h-4 w-4 text-gray-500" />
                    <span className="text-sm">Next: Photo post</span>
                  </>
                ) : (
                  <span className="text-sm">Manual content selection</span>
                )}
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-sm">
                  {autoSettings.platforms.length} platforms active
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <Badge variant={autoSettings.enabled ? "default" : "secondary"}>
                  {autoSettings.enabled ? "Active" : "Paused"}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Calendar Sidebar */}
          <Card>
            <CardHeader>
              <CardTitle>Schedule Calendar</CardTitle>
            </CardHeader>
            <CardContent>
              <Calendar
                mode="single"
                selected={selectedDate}
                onSelect={(date) => date && setSelectedDate(date)}
                className="rounded-md border"
              />
              <div className="mt-4 space-y-2">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-blue-500 rounded-full" />
                  <span className="text-sm text-gray-600">Scheduled</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full" />
                  <span className="text-sm text-gray-600">Published</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-yellow-500 rounded-full" />
                  <span className="text-sm text-gray-600">Pending Review</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Main Content Area */}
          <div className="lg:col-span-3">
            <Tabs value={viewMode} onValueChange={(value) => setViewMode(value as "calendar" | "list")}>
              <div className="flex items-center justify-between mb-4">
                <TabsList>
                  <TabsTrigger value="calendar">Calendar View</TabsTrigger>
                  <TabsTrigger value="list">List View</TabsTrigger>
                </TabsList>
                <div className="flex items-center space-x-2">
                  <Button variant="outline" size="sm">
                    <ChevronLeft className="h-4 w-4" />
                  </Button>
                  <span className="text-sm font-medium">
                    {format(selectedDate, "MMMM yyyy")}
                  </span>
                  <Button variant="outline" size="sm">
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              <TabsContent value="calendar" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>
                      {format(selectedDate, "EEEE, MMMM d, yyyy")}
                    </CardTitle>
                    <CardDescription>
                      {getPostsForDate(selectedDate).length} posts scheduled for this day
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {getPostsForDate(selectedDate).length > 0 ? (
                        getPostsForDate(selectedDate).map((post) => (
                          <div key={post.id} className="flex items-start space-x-4 p-4 border rounded-lg">
                            <div className="flex-shrink-0">
                              {post.type === "photo" ? (
                                <img
                                  src={post.imageUrl}
                                  alt="Post preview"
                                  className="w-16 h-16 object-cover rounded-lg"
                                />
                              ) : (
                                <div className="w-16 h-16 bg-gray-200 rounded-lg flex items-center justify-center relative">
                                  <img
                                    src={post.thumbnailUrl}
                                    alt="Video thumbnail"
                                    className="w-full h-full object-cover rounded-lg"
                                  />
                                  <div className="absolute inset-0 flex items-center justify-center">
                                    <Play className="h-6 w-6 text-white" />
                                  </div>
                                </div>
                              )}
                            </div>
                            <div className="flex-1">
                              <div className="flex items-center space-x-2 mb-2">
                                {getPlatformIcon(post.platform)}
                                <span className="text-sm font-medium">{post.platform}</span>
                                <Badge variant={post.type === "photo" ? "default" : "secondary"}>
                                  {post.type === "photo" ? (
                                    <Image className="h-3 w-3 mr-1" />
                                  ) : (
                                    <Video className="h-3 w-3 mr-1" />
                                  )}
                                  {post.type}
                                </Badge>
                                <span className="text-sm text-gray-500">
                                  {format(post.date, "h:mm a")}
                                </span>
                                <Badge variant="outline" className="text-xs">
                                  {post.engagement.estimated} engagement
                                </Badge>
                              </div>
                              <p className="text-sm text-gray-700 mb-2 line-clamp-2">
                                {post.content}
                              </p>
                              <div className="flex space-x-2">
                                <Button variant="ghost" size="sm">
                                  <Edit className="h-3 w-3 mr-1" />
                                  Edit
                                </Button>
                                <Button variant="ghost" size="sm">
                                  <Trash2 className="h-3 w-3 mr-1" />
                                  Delete
                                </Button>
                                <Button variant="ghost" size="sm">
                                  <BarChart3 className="h-3 w-3 mr-1" />
                                  Analytics
                                </Button>
                              </div>
                            </div>
                          </div>
                        ))
                      ) : (
                        <div className="text-center py-8">
                          <CalendarIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                          <p className="text-gray-500">No posts scheduled for this day</p>
                          <Button className="mt-2">
                            <Plus className="h-4 w-4 mr-2" />
                            Schedule Post
                          </Button>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="list" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>All Scheduled Posts</CardTitle>
                    <CardDescription>Complete list of upcoming scheduled content</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {scheduledPosts.map((post) => (
                        <div key={post.id} className="flex items-start space-x-4 p-4 border rounded-lg">
                          <div className="flex-shrink-0">
                            {post.type === "photo" ? (
                              <img
                                src={post.imageUrl}
                                alt="Post preview"
                                className="w-16 h-16 object-cover rounded-lg"
                              />
                            ) : (
                              <div className="w-16 h-16 bg-gray-200 rounded-lg flex items-center justify-center relative">
                                <img
                                  src={post.thumbnailUrl}
                                  alt="Video thumbnail"
                                  className="w-full h-full object-cover rounded-lg"
                                />
                                <div className="absolute inset-0 flex items-center justify-center">
                                  <Play className="h-6 w-6 text-white" />
                                </div>
                              </div>
                            )}
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-2">
                              {getPlatformIcon(post.platform)}
                              <span className="text-sm font-medium">{post.platform}</span>
                              <Badge variant={post.type === "photo" ? "default" : "secondary"}>
                                {post.type === "photo" ? (
                                  <Image className="h-3 w-3 mr-1" />
                                ) : (
                                  <Video className="h-3 w-3 mr-1" />
                                )}
                                {post.type}
                              </Badge>
                              <span className="text-sm text-gray-500">
                                {format(post.date, "MMM d, h:mm a")}
                              </span>
                            </div>
                            <p className="text-sm text-gray-700 mb-2">
                              {post.content}
                            </p>
                            <div className="flex items-center justify-between">
                              <Badge variant="outline" className="text-xs">
                                {post.engagement.estimated} engagement expected
                              </Badge>
                              <div className="flex space-x-2">
                                <Button variant="ghost" size="sm">
                                  <Edit className="h-3 w-3" />
                                </Button>
                                <Button variant="ghost" size="sm">
                                  <Trash2 className="h-3 w-3" />
                                </Button>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </div>

        {/* Automation Settings */}
        <Card>
          <CardHeader>
            <CardTitle>Automation Rules</CardTitle>
            <CardDescription>Configure intelligent posting schedules</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="space-y-4">
                <h4 className="font-medium">Posting Frequency</h4>
                <div className="space-y-2">
                  <Label>Posts per day</Label>
                  <Select value={autoSettings.timesPerDay.toString()} onValueChange={(value) =>
                    setAutoSettings({...autoSettings, timesPerDay: parseInt(value)})
                  }>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">1 time per day</SelectItem>
                      <SelectItem value="2">2 times per day</SelectItem>
                      <SelectItem value="3">3 times per day</SelectItem>
                      <SelectItem value="4">4 times per day</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="font-medium">Posting Times</h4>
                <div className="space-y-2">
                  <Label>First post time</Label>
                  <Select value={autoSettings.firstPost} onValueChange={(value) =>
                    setAutoSettings({...autoSettings, firstPost: value})
                  }>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {timeSlots.map(time => (
                        <SelectItem key={time} value={time}>{time}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Second post time</Label>
                  <Select value={autoSettings.secondPost} onValueChange={(value) =>
                    setAutoSettings({...autoSettings, secondPost: value})
                  }>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {timeSlots.map(time => (
                        <SelectItem key={time} value={time}>{time}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="font-medium">Content Rules</h4>
                <div className="flex items-center space-x-2">
                  <Switch
                    checked={autoSettings.alternateContent}
                    onCheckedChange={(checked) => setAutoSettings({...autoSettings, alternateContent: checked})}
                  />
                  <Label>Alternate photo/video posts</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    checked={autoSettings.weekendPosting}
                    onCheckedChange={(checked) => setAutoSettings({...autoSettings, weekendPosting: checked})}
                  />
                  <Label>Post on weekends</Label>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Performance Overview */}
        <Card>
          <CardHeader>
            <CardTitle>Scheduling Performance</CardTitle>
            <CardDescription>How your scheduled content is performing</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">47</div>
                <div className="text-sm text-gray-500">Posts This Month</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">94%</div>
                <div className="text-sm text-gray-500">On-Time Delivery</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">+23%</div>
                <div className="text-sm text-gray-500">Engagement vs Manual</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">3.2hrs</div>
                <div className="text-sm text-gray-500">Time Saved Weekly</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
