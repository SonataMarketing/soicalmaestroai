"use client";

import { useState } from "react";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Label } from "@/components/ui/label";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  CheckCircle,
  XCircle,
  Clock,
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
  AlertTriangle,
  Edit,
  Calendar,
  Image,
  Video,
  Instagram,
  Twitter,
  Facebook,
  Linkedin,
  User,
  Flag,
  Send,
  Trash2
} from "lucide-react";
import { format } from "date-fns";

const reviewQueue = [
  {
    id: 1,
    type: "photo",
    platform: "Instagram",
    content: "🚀 Exciting news! Our AI-powered content generator just got smarter. Now it can analyze your brand voice and create content that sounds authentically you. What do you think about AI writing in your brand's voice?",
    imageUrl: "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400&h=400&fit=crop",
    hashtags: ["#AIContent", "#BrandVoice", "#Innovation", "#SocialMedia"],
    scheduledFor: new Date(2024, 7, 23, 10, 0),
    submittedBy: "AI Generator",
    submittedAt: new Date(2024, 7, 22, 14, 30),
    status: "pending",
    priority: "high",
    brandAlignment: 92,
    riskScore: "low",
    feedback: [],
    estimatedEngagement: "High"
  },
  {
    id: 2,
    type: "video",
    platform: "LinkedIn",
    content: "The future of content marketing lies in the perfect blend of human creativity and AI efficiency. Here's how companies are achieving 3x faster content production while maintaining authentic brand voice. What's your experience with AI tools?",
    thumbnailUrl: "https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=400&h=400&fit=crop",
    scheduledFor: new Date(2024, 7, 23, 16, 0),
    submittedBy: "AI Generator",
    submittedAt: new Date(2024, 7, 22, 15, 45),
    status: "pending",
    priority: "medium",
    brandAlignment: 87,
    riskScore: "low",
    feedback: [],
    estimatedEngagement: "Medium"
  },
  {
    id: 3,
    type: "photo",
    platform: "Twitter",
    content: "Breaking: AI content tools are revolutionizing how brands create and distribute content. The results? 340% increase in engagement and 60% reduction in production time. 🔥 #AIMarketing #ContentStrategy",
    imageUrl: "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400&h=400&fit=crop",
    hashtags: ["#AIMarketing", "#ContentStrategy", "#MarTech"],
    scheduledFor: new Date(2024, 7, 24, 9, 0),
    submittedBy: "AI Generator",
    submittedAt: new Date(2024, 7, 22, 16, 20),
    status: "flagged",
    priority: "high",
    brandAlignment: 78,
    riskScore: "medium",
    feedback: [
      {
        reviewer: "Sarah Chen",
        comment: "The statistics need verification. Can we confirm the 340% increase claim?",
        timestamp: new Date(2024, 7, 22, 17, 30),
        type: "concern"
      }
    ],
    estimatedEngagement: "High"
  }
];

const approvedContent = [
  {
    id: 101,
    type: "photo",
    platform: "Instagram",
    content: "Monday motivation: Your brand's voice is unique, and AI should amplify it, not replace it. Here's how we're helping brands maintain authenticity while scaling content production...",
    imageUrl: "https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=400&h=400&fit=crop",
    approvedBy: "Marketing Manager",
    approvedAt: new Date(2024, 7, 22, 11, 15),
    publishedAt: new Date(2024, 7, 22, 12, 0),
    performance: { likes: 247, comments: 18, shares: 12 }
  }
];

const reviewers = [
  { id: 1, name: "Sarah Chen", role: "Marketing Manager", avatar: "/avatars/sarah.jpg" },
  { id: 2, name: "Mike Rodriguez", role: "Content Director", avatar: "/avatars/mike.jpg" },
  { id: 3, name: "Emma Thompson", role: "Brand Manager", avatar: "/avatars/emma.jpg" }
];

export default function ReviewQueue() {
  const [selectedItem, setSelectedItem] = useState<number | null>(null);
  const [reviewComment, setReviewComment] = useState("");
  const [filterStatus, setFilterStatus] = useState("all");

  const handleApprove = (id: number) => {
    console.log("Approved content:", id);
    // Handle approval logic
  };

  const handleReject = (id: number) => {
    console.log("Rejected content:", id);
    // Handle rejection logic
  };

  const handleFlag = (id: number) => {
    console.log("Flagged content:", id);
    // Handle flagging logic
  };

  const addFeedback = (id: number) => {
    if (reviewComment.trim()) {
      console.log("Adding feedback:", { id, comment: reviewComment });
      setReviewComment("");
    }
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

  const filteredQueue = reviewQueue.filter(item => {
    if (filterStatus === "all") return true;
    return item.status === filterStatus;
  });

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Review Queue</h1>
            <p className="text-gray-600">Review and approve AI-generated content before publishing</p>
          </div>
          <div className="flex items-center space-x-3">
            <Select value={filterStatus} onValueChange={setFilterStatus}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Content</SelectItem>
                <SelectItem value="pending">Pending Review</SelectItem>
                <SelectItem value="flagged">Flagged</SelectItem>
                <SelectItem value="approved">Approved</SelectItem>
                <SelectItem value="rejected">Rejected</SelectItem>
              </SelectContent>
            </Select>
            <Badge variant="destructive" className="text-sm">
              {reviewQueue.filter(item => item.status === "pending").length} pending
            </Badge>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <Clock className="h-5 w-5 text-yellow-500" />
                <div>
                  <div className="text-2xl font-bold">{reviewQueue.filter(item => item.status === "pending").length}</div>
                  <div className="text-sm text-gray-500">Pending Review</div>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <div>
                  <div className="text-2xl font-bold">23</div>
                  <div className="text-sm text-gray-500">Approved Today</div>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="h-5 w-5 text-red-500" />
                <div>
                  <div className="text-2xl font-bold">{reviewQueue.filter(item => item.status === "flagged").length}</div>
                  <div className="text-sm text-gray-500">Flagged Items</div>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-2">
                <ThumbsUp className="h-5 w-5 text-blue-500" />
                <div>
                  <div className="text-2xl font-bold">94%</div>
                  <div className="text-sm text-gray-500">Approval Rate</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="queue" className="space-y-6">
          <TabsList>
            <TabsTrigger value="queue">Review Queue</TabsTrigger>
            <TabsTrigger value="approved">Approved Content</TabsTrigger>
            <TabsTrigger value="analytics">Review Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="queue" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Content List */}
              <div className="lg:col-span-2 space-y-4">
                {filteredQueue.map((item) => (
                  <Card
                    key={item.id}
                    className={`cursor-pointer transition-all ${
                      selectedItem === item.id ? "ring-2 ring-blue-500" : ""
                    } ${
                      item.status === "flagged" ? "border-red-200 bg-red-50" : ""
                    }`}
                    onClick={() => setSelectedItem(item.id)}
                  >
                    <CardContent className="p-6">
                      <div className="flex items-start space-x-4">
                        <div className="flex-shrink-0">
                          {item.type === "photo" ? (
                            <img
                              src={item.imageUrl}
                              alt="Content preview"
                              className="w-20 h-20 object-cover rounded-lg"
                            />
                          ) : (
                            <div className="w-20 h-20 bg-gray-200 rounded-lg flex items-center justify-center relative">
                              <img
                                src={item.thumbnailUrl}
                                alt="Video thumbnail"
                                className="w-full h-full object-cover rounded-lg"
                              />
                              <div className="absolute inset-0 flex items-center justify-center">
                                <Video className="h-6 w-6 text-white" />
                              </div>
                            </div>
                          )}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            {getPlatformIcon(item.platform)}
                            <span className="text-sm font-medium">{item.platform}</span>
                            <Badge variant={item.type === "photo" ? "default" : "secondary"}>
                              {item.type === "photo" ? (
                                <Image className="h-3 w-3 mr-1" />
                              ) : (
                                <Video className="h-3 w-3 mr-1" />
                              )}
                              {item.type}
                            </Badge>
                            <Badge variant={
                              item.status === "pending" ? "secondary" :
                              item.status === "flagged" ? "destructive" : "default"
                            }>
                              {item.status}
                            </Badge>
                            <Badge variant={
                              item.priority === "high" ? "destructive" :
                              item.priority === "medium" ? "default" : "secondary"
                            } className="text-xs">
                              {item.priority} priority
                            </Badge>
                          </div>
                          <p className="text-sm text-gray-700 mb-3 line-clamp-3">
                            {item.content}
                          </p>
                          <div className="flex items-center justify-between text-xs text-gray-500">
                            <span>Scheduled: {format(item.scheduledFor, "MMM d, h:mm a")}</span>
                            <span>Brand alignment: {item.brandAlignment}%</span>
                          </div>
                          {item.feedback.length > 0 && (
                            <div className="mt-2 p-2 bg-yellow-50 rounded border-l-2 border-yellow-500">
                              <div className="flex items-center space-x-1 text-xs text-yellow-700">
                                <MessageSquare className="h-3 w-3" />
                                <span>{item.feedback.length} feedback comment(s)</span>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* Review Panel */}
              <div className="space-y-4">
                {selectedItem ? (
                  <>
                    {(() => {
                      const item = reviewQueue.find(i => i.id === selectedItem);
                      if (!item) return null;

                      return (
                        <>
                          <Card>
                            <CardHeader>
                              <CardTitle className="text-lg">Review Actions</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                              <div className="grid grid-cols-2 gap-2">
                                <Button
                                  onClick={() => handleApprove(item.id)}
                                  className="bg-green-600 hover:bg-green-700"
                                >
                                  <CheckCircle className="h-4 w-4 mr-2" />
                                  Approve
                                </Button>
                                <Button
                                  variant="destructive"
                                  onClick={() => handleReject(item.id)}
                                >
                                  <XCircle className="h-4 w-4 mr-2" />
                                  Reject
                                </Button>
                              </div>
                              <div className="grid grid-cols-2 gap-2">
                                <Button
                                  variant="outline"
                                  onClick={() => handleFlag(item.id)}
                                >
                                  <Flag className="h-4 w-4 mr-2" />
                                  Flag
                                </Button>
                                <Button variant="outline">
                                  <Edit className="h-4 w-4 mr-2" />
                                  Edit
                                </Button>
                              </div>
                              <Button variant="outline" className="w-full">
                                <Calendar className="h-4 w-4 mr-2" />
                                Reschedule
                              </Button>
                            </CardContent>
                          </Card>

                          <Card>
                            <CardHeader>
                              <CardTitle className="text-lg">Content Analysis</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                              <div className="space-y-2">
                                <div className="flex justify-between text-sm">
                                  <span>Brand Alignment</span>
                                  <span className="font-medium">{item.brandAlignment}%</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                  <span>Risk Score</span>
                                  <Badge variant={
                                    item.riskScore === "low" ? "default" :
                                    item.riskScore === "medium" ? "secondary" : "destructive"
                                  }>
                                    {item.riskScore}
                                  </Badge>
                                </div>
                                <div className="flex justify-between text-sm">
                                  <span>Expected Engagement</span>
                                  <span className="font-medium">{item.estimatedEngagement}</span>
                                </div>
                              </div>
                            </CardContent>
                          </Card>

                          <Card>
                            <CardHeader>
                              <CardTitle className="text-lg">Add Feedback</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                              <Textarea
                                placeholder="Add your review comments..."
                                value={reviewComment}
                                onChange={(e) => setReviewComment(e.target.value)}
                                className="min-h-[100px]"
                              />
                              <Button
                                onClick={() => addFeedback(item.id)}
                                disabled={!reviewComment.trim()}
                                className="w-full"
                              >
                                <Send className="h-4 w-4 mr-2" />
                                Add Feedback
                              </Button>
                            </CardContent>
                          </Card>

                          {item.feedback.length > 0 && (
                            <Card>
                              <CardHeader>
                                <CardTitle className="text-lg">Previous Feedback</CardTitle>
                              </CardHeader>
                              <CardContent className="space-y-3">
                                {item.feedback.map((feedback, index) => (
                                  <div key={index} className="p-3 border rounded-lg">
                                    <div className="flex items-center space-x-2 mb-2">
                                      <Avatar className="h-6 w-6">
                                        <AvatarFallback className="text-xs">
                                          {feedback.reviewer.split(' ').map(n => n[0]).join('')}
                                        </AvatarFallback>
                                      </Avatar>
                                      <span className="text-sm font-medium">{feedback.reviewer}</span>
                                      <span className="text-xs text-gray-500">
                                        {format(feedback.timestamp, "MMM d, h:mm a")}
                                      </span>
                                    </div>
                                    <p className="text-sm text-gray-700">{feedback.comment}</p>
                                  </div>
                                ))}
                              </CardContent>
                            </Card>
                          )}
                        </>
                      );
                    })()}
                  </>
                ) : (
                  <Card>
                    <CardContent className="p-6 text-center">
                      <User className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-500">Select content from the queue to review</p>
                    </CardContent>
                  </Card>
                )}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="approved" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Recently Approved Content</CardTitle>
                <CardDescription>Content that has been approved and published</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {approvedContent.map((item) => (
                    <div key={item.id} className="flex items-start space-x-4 p-4 border rounded-lg bg-green-50">
                      <img
                        src={item.imageUrl}
                        alt="Approved content"
                        className="w-16 h-16 object-cover rounded-lg"
                      />
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          {getPlatformIcon(item.platform)}
                          <span className="text-sm font-medium">{item.platform}</span>
                          <Badge variant="default" className="bg-green-600">
                            <CheckCircle className="h-3 w-3 mr-1" />
                            Approved
                          </Badge>
                          <span className="text-sm text-gray-500">
                            by {item.approvedBy}
                          </span>
                        </div>
                        <p className="text-sm text-gray-700 mb-2">{item.content}</p>
                        <div className="flex items-center space-x-4 text-xs text-gray-500">
                          <span>Published: {format(item.publishedAt, "MMM d, h:mm a")}</span>
                          <span>{item.performance.likes} likes</span>
                          <span>{item.performance.comments} comments</span>
                          <span>{item.performance.shares} shares</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Review Performance</CardTitle>
                <CardDescription>Analytics on the review process and content quality</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900">2.3hrs</div>
                    <div className="text-sm text-gray-500">Avg Review Time</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900">94%</div>
                    <div className="text-sm text-gray-500">Approval Rate</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900">156</div>
                    <div className="text-sm text-gray-500">Items Reviewed</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900">+23%</div>
                    <div className="text-sm text-gray-500">Quality Improvement</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}
