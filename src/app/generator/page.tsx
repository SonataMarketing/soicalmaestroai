"use client";

import { useState } from "react";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import {
  Wand2,
  Copy,
  RefreshCw,
  Save,
  Calendar,
  Image,
  Video,
  Type,
  Palette,
  Target,
  TrendingUp,
  Sparkles,
  Download,
  Share
} from "lucide-react";

const contentTypes = [
  { value: "post", label: "Social Media Post", icon: Type },
  { value: "story", label: "Story Content", icon: Image },
  { value: "video", label: "Video Script", icon: Video },
  { value: "caption", label: "Caption Only", icon: Type },
];

const toneOptions = [
  "Professional", "Casual", "Friendly", "Inspiring", "Educational",
  "Humorous", "Urgent", "Grateful", "Exciting", "Thoughtful"
];

const platforms = [
  { value: "instagram", label: "Instagram", limit: 2200 },
  { value: "twitter", label: "Twitter", limit: 280 },
  { value: "linkedin", label: "LinkedIn", limit: 3000 },
  { value: "facebook", label: "Facebook", limit: 8000 },
];

const generatedContent = [
  {
    id: 1,
    type: "Instagram Post",
    content: "🚀 The future of content creation is here! Our AI-powered tools are transforming how brands connect with their audiences. From personalized captions to trend analysis, we're making social media management smarter and more efficient.\n\nWhat's your biggest challenge in content creation? Let us know in the comments! 👇\n\n#AIContent #SocialMediaMarketing #DigitalTransformation #ContentCreation #Innovation",
    hashtags: ["#AIContent", "#SocialMediaMarketing", "#DigitalTransformation"],
    metrics: { engagement: "High", brandAlignment: 94, trending: true },
    timestamp: "Generated 2 minutes ago"
  },
  {
    id: 2,
    type: "LinkedIn Post",
    content: "The landscape of digital marketing is evolving rapidly, and AI is at the forefront of this transformation. Companies that embrace AI-driven content strategies are seeing:\n\n• 340% increase in engagement rates\n• 67% reduction in content creation time\n• 85% improvement in brand consistency\n\nAt our company, we've witnessed firsthand how intelligent automation can amplify human creativity. The key is finding the right balance between efficiency and authenticity.\n\nWhat's your experience with AI in marketing? I'd love to hear your thoughts.",
    hashtags: ["#DigitalMarketing", "#AI", "#ContentStrategy"],
    metrics: { engagement: "Medium", brandAlignment: 89, trending: false },
    timestamp: "Generated 5 minutes ago"
  }
];

const templateSuggestions = [
  { name: "Product Launch", description: "Announce new products with excitement" },
  { name: "Behind the Scenes", description: "Show your company culture" },
  { name: "Educational Tip", description: "Share valuable insights" },
  { name: "User Generated Content", description: "Feature customer stories" },
  { name: "Trending Topic", description: "Join current conversations" },
  { name: "Question Post", description: "Engage with your audience" }
];

export default function ContentGenerator() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [prompt, setPrompt] = useState("");
  const [selectedPlatform, setSelectedPlatform] = useState("instagram");
  const [selectedTone, setSelectedTone] = useState("Professional");
  const [contentLength, setContentLength] = useState([150]);
  const [includeHashtags, setIncludeHashtags] = useState(true);
  const [includeEmojis, setIncludeEmojis] = useState(true);
  const [selectedTemplate, setSelectedTemplate] = useState("");

  const handleGenerate = async () => {
    setIsGenerating(true);
    // Simulate AI generation
    setTimeout(() => setIsGenerating(false), 3000);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">AI Content Generator</h1>
            <p className="text-gray-600">Create engaging content that matches your brand voice</p>
          </div>
          <div className="flex space-x-3">
            <Button variant="outline">
              <Save className="h-4 w-4 mr-2" />
              Save Template
            </Button>
            <Button>
              <Calendar className="h-4 w-4 mr-2" />
              Schedule Generated
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Content Generator Form */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Generate New Content</CardTitle>
              <CardDescription>Describe what you want to create and let AI do the magic</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Quick Templates */}
              <div>
                <Label className="text-sm font-medium mb-3 block">Quick Templates</Label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {templateSuggestions.map((template, index) => (
                    <Button
                      key={index}
                      variant={selectedTemplate === template.name ? "default" : "outline"}
                      size="sm"
                      onClick={() => setSelectedTemplate(template.name)}
                      className="text-xs"
                    >
                      {template.name}
                    </Button>
                  ))}
                </div>
              </div>

              <Separator />

              {/* Content Prompt */}
              <div>
                <Label htmlFor="prompt" className="text-sm font-medium mb-2 block">
                  Content Description
                </Label>
                <Textarea
                  id="prompt"
                  placeholder="Describe the content you want to generate... (e.g., 'Create a post about our new AI features that highlights innovation and user benefits')"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  className="min-h-[100px]"
                />
              </div>

              {/* Platform & Settings */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium mb-2 block">Platform</Label>
                  <Select value={selectedPlatform} onValueChange={setSelectedPlatform}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {platforms.map((platform) => (
                        <SelectItem key={platform.value} value={platform.value}>
                          {platform.label} ({platform.limit} chars)
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label className="text-sm font-medium mb-2 block">Tone</Label>
                  <Select value={selectedTone} onValueChange={setSelectedTone}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {toneOptions.map((tone) => (
                        <SelectItem key={tone} value={tone}>
                          {tone}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Content Length */}
              <div>
                <Label className="text-sm font-medium mb-4 block">
                  Content Length: {contentLength[0]} characters
                </Label>
                <Slider
                  value={contentLength}
                  onValueChange={setContentLength}
                  max={platforms.find(p => p.value === selectedPlatform)?.limit || 2200}
                  min={50}
                  step={10}
                  className="w-full"
                />
              </div>

              {/* Additional Options */}
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center space-x-2">
                  <Switch
                    id="hashtags"
                    checked={includeHashtags}
                    onCheckedChange={setIncludeHashtags}
                  />
                  <Label htmlFor="hashtags" className="text-sm">Include hashtags</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="emojis"
                    checked={includeEmojis}
                    onCheckedChange={setIncludeEmojis}
                  />
                  <Label htmlFor="emojis" className="text-sm">Include emojis</Label>
                </div>
              </div>

              <Button
                onClick={handleGenerate}
                disabled={isGenerating || !prompt.trim()}
                className="w-full"
                size="lg"
              >
                {isGenerating ? (
                  <RefreshCw className="h-5 w-5 mr-2 animate-spin" />
                ) : (
                  <Wand2 className="h-5 w-5 mr-2" />
                )}
                {isGenerating ? "Generating Content..." : "Generate Content"}
              </Button>
            </CardContent>
          </Card>

          {/* Brand Guidelines Sidebar */}
          <Card>
            <CardHeader>
              <CardTitle>Brand Guidelines</CardTitle>
              <CardDescription>AI will use these guidelines for content generation</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Brand Voice</span>
                  <Badge variant="secondary">Professional</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Primary Audience</span>
                  <Badge variant="secondary">B2B Tech</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Content Style</span>
                  <Badge variant="secondary">Educational</Badge>
                </div>
              </div>

              <Separator />

              <div>
                <h4 className="text-sm font-medium mb-2">Key Themes</h4>
                <div className="flex flex-wrap gap-1">
                  <Badge variant="outline" className="text-xs">Innovation</Badge>
                  <Badge variant="outline" className="text-xs">Technology</Badge>
                  <Badge variant="outline" className="text-xs">Efficiency</Badge>
                  <Badge variant="outline" className="text-xs">Growth</Badge>
                </div>
              </div>

              <div>
                <h4 className="text-sm font-medium mb-2">Avoid Keywords</h4>
                <div className="flex flex-wrap gap-1">
                  <Badge variant="destructive" className="text-xs">Boring</Badge>
                  <Badge variant="destructive" className="text-xs">Cheap</Badge>
                  <Badge variant="destructive" className="text-xs">Basic</Badge>
                </div>
              </div>

              <Separator />

              <Button variant="outline" className="w-full" size="sm">
                <Palette className="h-4 w-4 mr-2" />
                View Full Guidelines
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Generated Content */}
        <Card>
          <CardHeader>
            <CardTitle>Generated Content</CardTitle>
            <CardDescription>Your AI-generated content ready for review and scheduling</CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="recent" className="space-y-4">
              <TabsList>
                <TabsTrigger value="recent">Recent Generations</TabsTrigger>
                <TabsTrigger value="saved">Saved Drafts</TabsTrigger>
                <TabsTrigger value="scheduled">Scheduled</TabsTrigger>
              </TabsList>

              <TabsContent value="recent" className="space-y-4">
                {generatedContent.map((content) => (
                  <Card key={content.id}>
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <Badge variant="secondary">{content.type}</Badge>
                          <span className="text-sm text-gray-500">{content.timestamp}</span>
                          {content.metrics.trending && (
                            <Badge variant="default" className="bg-green-600">
                              <TrendingUp className="h-3 w-3 mr-1" />
                              Trending
                            </Badge>
                          )}
                        </div>
                        <div className="flex space-x-2">
                          <Button variant="ghost" size="sm" onClick={() => copyToClipboard(content.content)}>
                            <Copy className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <RefreshCw className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Save className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>

                      <div className="space-y-4">
                        <div className="p-4 bg-gray-50 rounded-lg">
                          <p className="text-gray-800 whitespace-pre-wrap">{content.content}</p>
                        </div>

                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <div className="text-sm">
                              <span className="text-gray-500">Brand Alignment: </span>
                              <span className="font-medium text-green-600">{content.metrics.brandAlignment}%</span>
                            </div>
                            <div className="text-sm">
                              <span className="text-gray-500">Engagement Potential: </span>
                              <span className="font-medium">{content.metrics.engagement}</span>
                            </div>
                          </div>
                          <div className="flex space-x-2">
                            <Button variant="outline" size="sm">
                              <Calendar className="h-4 w-4 mr-1" />
                              Schedule
                            </Button>
                            <Button size="sm">
                              <Share className="h-4 w-4 mr-1" />
                              Publish Now
                            </Button>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </TabsContent>

              <TabsContent value="saved">
                <Card>
                  <CardContent className="p-6 text-center">
                    <p className="text-gray-500">No saved drafts yet. Generate some content and save your favorites!</p>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="scheduled">
                <Card>
                  <CardContent className="p-6 text-center">
                    <p className="text-gray-500">No scheduled content. Use the scheduler to plan your posts in advance.</p>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        {/* Performance Insights */}
        <Card>
          <CardHeader>
            <CardTitle>Generation Insights</CardTitle>
            <CardDescription>Performance metrics for your AI-generated content</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">156</div>
                <div className="text-sm text-gray-500">Content Pieces Generated</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">87%</div>
                <div className="text-sm text-gray-500">Average Brand Alignment</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">23</div>
                <div className="text-sm text-gray-500">Published This Week</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">+34%</div>
                <div className="text-sm text-gray-500">Engagement Increase</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
