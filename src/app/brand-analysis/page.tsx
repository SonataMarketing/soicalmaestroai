"use client";

import { useState } from "react";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import {
  TrendingUp,
  Palette,
  Type,
  Users,
  Target,
  Globe,
  Instagram,
  Twitter,
  Facebook,
  Linkedin,
  Eye,
  RefreshCw,
  Plus,
  BarChart3
} from "lucide-react";

const brandMetrics = [
  {
    category: "Brand Voice",
    score: 87,
    description: "Professional, friendly, and approachable tone",
    keywords: ["innovative", "reliable", "customer-focused", "authentic"],
    color: "bg-blue-500"
  },
  {
    category: "Visual Style",
    score: 92,
    description: "Modern, minimalist design with consistent color palette",
    keywords: ["clean", "modern", "blue", "white", "minimalist"],
    color: "bg-green-500"
  },
  {
    category: "Content Themes",
    score: 78,
    description: "Tech-focused with educational and industry insights",
    keywords: ["technology", "innovation", "tutorials", "industry news"],
    color: "bg-purple-500"
  },
  {
    category: "Audience Engagement",
    score: 84,
    description: "High engagement on educational content and behind-the-scenes",
    keywords: ["educational", "behind-the-scenes", "Q&A", "tips"],
    color: "bg-orange-500"
  }
];

const competitorAnalysis = [
  {
    name: "TechInnovate Corp",
    similarity: 73,
    strengths: ["Strong visual branding", "Consistent posting"],
    weaknesses: ["Limited engagement", "Repetitive content"],
    platforms: ["Instagram", "LinkedIn", "Twitter"]
  },
  {
    name: "Digital Solutions Pro",
    similarity: 68,
    strengths: ["High engagement rate", "Video content"],
    weaknesses: ["Inconsistent branding", "Limited reach"],
    platforms: ["Instagram", "Facebook", "YouTube"]
  },
  {
    name: "Innovation Hub",
    similarity: 61,
    strengths: ["Thought leadership", "Industry partnerships"],
    weaknesses: ["Low posting frequency", "Text-heavy content"],
    platforms: ["LinkedIn", "Twitter", "Medium"]
  }
];

const brandElements = {
  colors: [
    { name: "Primary Blue", hex: "#2563eb", usage: "45%" },
    { name: "Secondary Gray", hex: "#6b7280", usage: "25%" },
    { name: "Accent Orange", hex: "#f97316", usage: "15%" },
    { name: "White", hex: "#ffffff", usage: "15%" }
  ],
  fonts: [
    { name: "Inter", category: "Primary", usage: "Headlines & Body" },
    { name: "Roboto", category: "Secondary", usage: "Captions & Tags" }
  ],
  contentPillars: [
    { pillar: "Industry Insights", percentage: 35 },
    { pillar: "Product Updates", percentage: 25 },
    { pillar: "Company Culture", percentage: 20 },
    { pillar: "Educational Content", percentage: 20 }
  ]
};

const connectedAccounts = [
  { platform: "Instagram", handle: "@yourcompany", followers: "12.5K", status: "active" },
  { platform: "Twitter", handle: "@yourcompany", followers: "8.2K", status: "active" },
  { platform: "LinkedIn", handle: "Your Company", followers: "25.1K", status: "active" },
  { platform: "Facebook", handle: "Your Company", followers: "15.7K", status: "pending" }
];

export default function BrandAnalysis() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [websiteUrl, setWebsiteUrl] = useState("");

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    // Simulate AI analysis
    setTimeout(() => setIsAnalyzing(false), 3000);
  };

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Brand Analysis</h1>
            <p className="text-gray-600">AI-powered analysis of your brand identity and style</p>
          </div>
          <Button onClick={handleAnalyze} disabled={isAnalyzing}>
            {isAnalyzing ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <BarChart3 className="h-4 w-4 mr-2" />
            )}
            Analyze Brand
          </Button>
        </div>

        {/* Quick Setup */}
        <Card>
          <CardHeader>
            <CardTitle>Brand Analysis Setup</CardTitle>
            <CardDescription>Add your website and social accounts for comprehensive analysis</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex space-x-4">
              <Input
                placeholder="Enter your website URL"
                value={websiteUrl}
                onChange={(e) => setWebsiteUrl(e.target.value)}
                className="flex-1"
              />
              <Button variant="outline">
                <Globe className="h-4 w-4 mr-2" />
                Analyze Website
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {connectedAccounts.map((account, index) => (
                <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center space-x-2">
                    {account.platform === "Instagram" && <Instagram className="h-4 w-4 text-pink-500" />}
                    {account.platform === "Twitter" && <Twitter className="h-4 w-4 text-blue-500" />}
                    {account.platform === "LinkedIn" && <Linkedin className="h-4 w-4 text-blue-600" />}
                    {account.platform === "Facebook" && <Facebook className="h-4 w-4 text-blue-700" />}
                    <div>
                      <div className="text-sm font-medium">{account.platform}</div>
                      <div className="text-xs text-gray-500">{account.followers}</div>
                    </div>
                  </div>
                  <Badge variant={account.status === "active" ? "default" : "secondary"}>
                    {account.status}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList>
            <TabsTrigger value="overview">Brand Overview</TabsTrigger>
            <TabsTrigger value="visual">Visual Identity</TabsTrigger>
            <TabsTrigger value="voice">Brand Voice</TabsTrigger>
            <TabsTrigger value="competitors">Competitor Analysis</TabsTrigger>
            <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Brand Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {brandMetrics.map((metric) => (
                <Card key={metric.category}>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-gray-600">
                      {metric.category}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-2xl font-bold">{metric.score}%</span>
                        <div className={`w-3 h-3 rounded-full ${metric.color}`} />
                      </div>
                      <Progress value={metric.score} className="h-2" />
                      <p className="text-xs text-gray-600">{metric.description}</p>
                      <div className="flex flex-wrap gap-1">
                        {metric.keywords.slice(0, 2).map((keyword, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {keyword}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Content Performance */}
            <Card>
              <CardHeader>
                <CardTitle>Content Performance Insights</CardTitle>
                <CardDescription>How your content performs across different categories</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {brandElements.contentPillars.map((pillar, index) => (
                    <div key={index} className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="font-medium">{pillar.pillar}</span>
                        <span className="text-gray-500">{pillar.percentage}% of content</span>
                      </div>
                      <Progress value={pillar.percentage} className="h-2" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="visual" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Color Palette */}
              <Card>
                <CardHeader>
                  <CardTitle>Brand Colors</CardTitle>
                  <CardDescription>Your dominant color palette across platforms</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {brandElements.colors.map((color, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div
                          className="w-8 h-8 rounded-lg border"
                          style={{ backgroundColor: color.hex }}
                        />
                        <div>
                          <div className="font-medium">{color.name}</div>
                          <div className="text-sm text-gray-500">{color.hex}</div>
                        </div>
                      </div>
                      <Badge variant="outline">{color.usage}</Badge>
                    </div>
                  ))}
                </CardContent>
              </Card>

              {/* Typography */}
              <Card>
                <CardHeader>
                  <CardTitle>Typography</CardTitle>
                  <CardDescription>Font families used in your content</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {brandElements.fonts.map((font, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <div className="font-medium" style={{ fontFamily: font.name }}>
                          {font.name}
                        </div>
                        <div className="text-sm text-gray-500">{font.usage}</div>
                      </div>
                      <Badge variant="secondary">{font.category}</Badge>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>

            {/* Visual Guidelines */}
            <Card>
              <CardHeader>
                <CardTitle>Visual Guidelines</CardTitle>
                <CardDescription>AI-generated recommendations for consistent branding</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 border rounded-lg">
                    <h4 className="font-medium mb-2">Image Style</h4>
                    <p className="text-sm text-gray-600">Clean, minimal images with plenty of white space. Focus on product shots and professional photography.</p>
                  </div>
                  <div className="p-4 border rounded-lg">
                    <h4 className="font-medium mb-2">Logo Usage</h4>
                    <p className="text-sm text-gray-600">Use primary logo on light backgrounds. Maintain clear space equal to the logo height.</p>
                  </div>
                  <div className="p-4 border rounded-lg">
                    <h4 className="font-medium mb-2">Layout</h4>
                    <p className="text-sm text-gray-600">Grid-based layouts with consistent spacing. 8px base unit for all measurements.</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="voice" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Brand Voice Analysis</CardTitle>
                <CardDescription>AI analysis of your communication style and tone</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h4 className="font-medium">Voice Characteristics</h4>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Professional</span>
                        <Progress value={85} className="w-24 h-2" />
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Friendly</span>
                        <Progress value={72} className="w-24 h-2" />
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Informative</span>
                        <Progress value={90} className="w-24 h-2" />
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Conversational</span>
                        <Progress value={68} className="w-24 h-2" />
                      </div>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <h4 className="font-medium">Common Phrases</h4>
                    <div className="space-y-2">
                      <Badge variant="outline">"Let's dive into..."</Badge>
                      <Badge variant="outline">"We're excited to..."</Badge>
                      <Badge variant="outline">"Here's what you need to know"</Badge>
                      <Badge variant="outline">"Join us as we..."</Badge>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="competitors" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Competitor Analysis</CardTitle>
                <CardDescription>How your brand compares to similar companies</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {competitorAnalysis.map((competitor, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="font-medium">{competitor.name}</h4>
                        <Badge variant="outline">{competitor.similarity}% similar</Badge>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                          <h5 className="text-sm font-medium text-green-600 mb-2">Strengths</h5>
                          <ul className="text-sm text-gray-600 space-y-1">
                            {competitor.strengths.map((strength, i) => (
                              <li key={i}>• {strength}</li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <h5 className="text-sm font-medium text-red-600 mb-2">Weaknesses</h5>
                          <ul className="text-sm text-gray-600 space-y-1">
                            {competitor.weaknesses.map((weakness, i) => (
                              <li key={i}>• {weakness}</li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <h5 className="text-sm font-medium text-blue-600 mb-2">Platforms</h5>
                          <div className="flex flex-wrap gap-1">
                            {competitor.platforms.map((platform, i) => (
                              <Badge key={i} variant="secondary" className="text-xs">
                                {platform}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="recommendations" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>AI Recommendations</CardTitle>
                <CardDescription>Personalized suggestions to improve your brand presence</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="p-4 border-l-4 border-blue-500 bg-blue-50">
                    <h4 className="font-medium text-blue-900">Increase Visual Consistency</h4>
                    <p className="text-sm text-blue-700 mt-1">
                      Use your brand colors more consistently across posts. Consider creating templates for different content types.
                    </p>
                  </div>
                  <div className="p-4 border-l-4 border-green-500 bg-green-50">
                    <h4 className="font-medium text-green-900">Expand Content Pillars</h4>
                    <p className="text-sm text-green-700 mt-1">
                      Add more behind-the-scenes content to increase audience engagement and authenticity.
                    </p>
                  </div>
                  <div className="p-4 border-l-4 border-purple-500 bg-purple-50">
                    <h4 className="font-medium text-purple-900">Optimize Posting Times</h4>
                    <p className="text-sm text-purple-700 mt-1">
                      Your audience is most active on weekdays between 2-4 PM. Schedule more content during these peak hours.
                    </p>
                  </div>
                  <div className="p-4 border-l-4 border-orange-500 bg-orange-50">
                    <h4 className="font-medium text-orange-900">Video Content Opportunity</h4>
                    <p className="text-sm text-orange-700 mt-1">
                      Video posts show 3x higher engagement. Consider adding short-form videos to your content mix.
                    </p>
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
