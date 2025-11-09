"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Upload,
  FileText,
  Video,
  FileCode,
  Loader2,
  CheckCircle,
  AlertCircle,
  Users,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";

interface UploadStatus {
  type: "success" | "error" | "loading";
  message: string;
}

export default function IngestionPage() {
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [resumeText, setResumeText] = useState("");
  const [employeeName, setEmployeeName] = useState("");
  const [status, setStatus] = useState<UploadStatus | null>(null);

  const handleResumeUpload = async () => {
    if (!resumeFile && !resumeText) return;

    setStatus({ type: "loading", message: "Processing resume..." });

    try {
      const formData = new FormData();
      if (resumeFile) {
        formData.append("file", resumeFile);
      }

      const response = await fetch("http://localhost:8001/upload/resume", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (data.success) {
        setStatus({
          type: "success",
          message: "Resume uploaded successfully!",
        });
        setTimeout(() => setStatus(null), 3000);
      } else {
        throw new Error("Upload failed");
      }
    } catch (error) {
      setStatus({
        type: "error",
        message:
          "Failed to upload. Make sure the API server is running on port 8001.",
      });
    }
  };

  const handleVideoUpload = async () => {
    if (!videoFile) return;

    setStatus({ type: "loading", message: "Processing video..." });

    try {
      const formData = new FormData();
      formData.append("file", videoFile);

      const response = await fetch("http://localhost:8001/upload/video", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (data.success) {
        setStatus({ type: "success", message: "Video uploaded successfully!" });
        setTimeout(() => setStatus(null), 3000);
      } else {
        throw new Error("Upload failed");
      }
    } catch (error) {
      setStatus({
        type: "error",
        message: "Failed to upload video. Make sure the API server is running.",
      });
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Status Banner */}
      {status && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Card
            className={`border shadow-lg ${
              status.type === "success"
                ? "border-terminal-green/50 bg-terminal-green/10"
                : status.type === "error"
                ? "border-destructive/50 bg-destructive/10"
                : "border-primary/50 bg-primary/10"
            }`}
          >
            <CardContent className="pt-6">
              <div className="flex items-center gap-3 font-mono text-sm">
                <span className="text-muted-foreground">$</span>
                {status.type === "loading" && (
                  <Loader2 className="w-4 h-4 animate-spin text-primary" />
                )}
                {status.type === "success" && (
                  <CheckCircle className="w-4 h-4 text-terminal-green" />
                )}
                {status.type === "error" && (
                  <AlertCircle className="w-4 h-4 text-destructive" />
                )}
                <span
                  className={`${
                    status.type === "success"
                      ? "text-terminal-green"
                      : status.type === "error"
                      ? "text-destructive"
                      : "text-primary"
                  }`}
                >
                  {status.message}
                </span>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Info Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <Card className="border-2 border-primary/30 shadow-xl shadow-primary/10 bg-card/95 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-3 text-foreground text-lg">
              <div className="w-10 h-10 bg-linear-to-br from-primary to-purple-600 rounded-xl flex items-center justify-center shadow-md shadow-primary/20">
                <Upload className="w-5 h-5 text-primary-foreground" />
              </div>
              Multimodal Data Ingestion
            </CardTitle>
            <CardDescription className="text-sm">
              Build your talent graph from multiple data sources • Skills
              extraction and confidence scoring
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              <div className="px-4 py-2 rounded-lg bg-primary/10 border border-primary/30 text-xs font-semibold text-foreground flex items-center gap-2 hover:bg-primary/20 hover:shadow-md hover:shadow-primary/10 transition-all">
                <FileText className="w-4 h-4 text-primary" />
                Resumes
              </div>
              <div className="px-4 py-2 rounded-lg bg-primary/10 border border-primary/30 text-xs font-semibold text-foreground flex items-center gap-2 hover:bg-primary/20 hover:shadow-md hover:shadow-primary/10 transition-all">
                <Video className="w-4 h-4 text-primary" />
                Interviews
              </div>
              <div className="px-4 py-2 rounded-lg bg-primary/10 border border-primary/30 text-xs font-semibold text-foreground flex items-center gap-2 hover:bg-primary/20 hover:shadow-md hover:shadow-primary/10 transition-all">
                <FileCode className="w-4 h-4 text-primary" />
                Reviews
              </div>
              <div className="px-4 py-2 rounded-lg bg-primary/10 border border-primary/30 text-xs font-semibold text-foreground flex items-center gap-2 hover:bg-primary/20 hover:shadow-md hover:shadow-primary/10 transition-all">
                <Users className="w-4 h-4 text-primary" />
                LinkedIn
              </div>
              <div className="px-4 py-2 rounded-lg bg-primary/10 border border-primary/30 text-xs font-semibold text-foreground flex items-center gap-2 hover:bg-primary/20 hover:shadow-md hover:shadow-primary/10 transition-all">
                <FileCode className="w-4 h-4 text-primary" />
                GitHub
              </div>
              <div className="px-4 py-2 rounded-lg bg-primary/10 border border-primary/30 text-xs font-semibold text-foreground flex items-center gap-2 hover:bg-primary/20 hover:shadow-md hover:shadow-primary/10 transition-all">
                <FileText className="w-4 h-4 text-primary" />
                Briefs
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Employee Info */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="border border-border bg-card">
          <CardHeader>
            <CardTitle className="text-foreground font-mono text-sm">
              $ candidate --init
            </CardTitle>
            <CardDescription className="font-mono text-xs">
              talent_graph_node_identifier
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-xs font-mono text-muted-foreground mb-2 flex items-center gap-2 uppercase tracking-wider">
                <span className="text-primary">›</span>identifier
              </label>
              <div className="flex items-center gap-2 bg-background border border-border rounded-sm px-3 py-2 focus-within:border-primary transition-colors">
                <span className="text-primary font-mono text-sm">$</span>
                <Input
                  placeholder="alice_chen"
                  value={employeeName}
                  onChange={(e) => setEmployeeName(e.target.value)}
                  className="bg-transparent border-0 focus-visible:ring-0 focus-visible:ring-offset-0 font-mono text-sm"
                />
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Resume Upload */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Card className="border border-border bg-card hover:border-primary/50 transition-all">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-foreground font-mono text-sm">
              <span className="text-primary">$</span>
              process_resume --extract-skills
            </CardTitle>
            <CardDescription className="font-mono text-xs">
              explicit_skills • implicit_skills • confidence_score
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-xs font-mono text-muted-foreground mb-2 flex items-center gap-2 uppercase tracking-wider">
                <span className="text-primary">›</span>input_method
              </label>
              <div className="border border-dashed border-border rounded-sm p-8 text-center hover:border-primary transition-all bg-background group">
                <input
                  type="file"
                  accept=".pdf,.txt,.doc,.docx"
                  onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
                  className="hidden"
                  id="resume-upload"
                />
                <label htmlFor="resume-upload" className="cursor-pointer">
                  <FileText className="w-12 h-12 text-primary/60 group-hover:text-primary mx-auto mb-3 transition-colors" />
                  {resumeFile ? (
                    <p className="text-foreground font-medium font-mono text-sm">
                      › {resumeFile.name}
                    </p>
                  ) : (
                    <>
                      <p className="text-foreground font-medium font-mono text-sm">
                        $ upload_file
                      </p>
                      <p className="text-xs text-muted-foreground mt-1 font-mono">
                        .pdf .txt .doc .docx &lt; 10MB
                      </p>
                    </>
                  )}
                </label>
              </div>
            </div>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-border" />
              </div>
              <div className="relative flex justify-center text-xs">
                <span className="bg-card px-3 text-muted-foreground font-mono uppercase tracking-wider">
                  or
                </span>
              </div>
            </div>

            <div>
              <Textarea
                placeholder="# Paste resume content\nname: Alice Chen\nskills: [Python, React, Docker]..."
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                rows={8}
                className="bg-background border-border focus:border-primary font-mono text-xs"
              />
            </div>

            <Button
              onClick={handleResumeUpload}
              className="w-full bg-primary/10 hover:bg-primary/20 border border-primary/30 text-primary font-mono uppercase text-xs tracking-wider"
              disabled={!resumeFile && !resumeText}
            >
              <Upload className="mr-2 h-4 w-4" />
              exec process
            </Button>
          </CardContent>
        </Card>
      </motion.div>

      {/* Video Upload */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Card className="border border-border bg-card hover:border-primary/50 transition-all">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-foreground font-mono text-sm">
              <span className="text-primary">$</span>
              process_video --multimodal
            </CardTitle>
            <CardDescription className="font-mono text-xs">
              audio_transcript • visual_analysis • behavioral_signals
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary transition-all bg-background/50">
              <input
                type="file"
                accept="video/*"
                onChange={(e) => setVideoFile(e.target.files?.[0] || null)}
                className="hidden"
                id="video-upload"
              />
              <label htmlFor="video-upload" className="cursor-pointer">
                <Video className="w-12 h-12 text-primary/60 mx-auto mb-3" />
                {videoFile ? (
                  <p className="text-foreground font-medium">
                    {videoFile.name}
                  </p>
                ) : (
                  <>
                    <p className="text-foreground font-medium">
                      Click to upload video
                    </p>
                    <p className="text-sm text-muted-foreground mt-1">
                      MP4, MOV, AVI up to 100MB
                    </p>
                  </>
                )}
              </label>
            </div>

            <Button
              onClick={handleVideoUpload}
              className="w-full bg-primary hover:bg-primary/90"
              disabled={!videoFile}
            >
              <Upload className="mr-2 h-4 w-4" />
              Process Video
            </Button>
          </CardContent>
        </Card>
      </motion.div>

      {/* Additional Sources */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Card className="border-primary/20 bg-card/80 backdrop-blur hover:border-primary/40 transition-all">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-foreground">
              <FileCode className="w-5 h-5 text-primary" />
              Additional Data Sources
            </CardTitle>
            <CardDescription>
              Multi-source validation for confidence boosting
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium text-foreground mb-2 flex items-center gap-2">
                <span className="text-primary">›</span>LinkedIn Profile
              </label>
              <Input
                placeholder="https://linkedin.com/in/..."
                className="bg-background/50 border-border focus:border-primary font-mono text-sm"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-foreground mb-2 flex items-center gap-2">
                <span className="text-primary">›</span>GitHub Profile
              </label>
              <Input
                placeholder="https://github.com/..."
                className="bg-background/50 border-border focus:border-primary font-mono text-sm"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-foreground mb-2 flex items-center gap-2">
                <span className="text-primary">›</span>Performance Review
              </label>
              <Textarea
                placeholder="Paste review content for implicit skill extraction..."
                rows={6}
                className="bg-background/50 border-border focus:border-primary font-mono text-sm"
              />
            </div>
            <Button className="w-full bg-linear-to-r from-primary to-purple-600 hover:from-primary/90 hover:to-purple-600/90 shadow-md shadow-primary/20 hover:shadow-lg hover:shadow-primary/30 transition-all duration-300 text-primary-foreground font-semibold">
              <Upload className="mr-2 h-5 w-5" />
              Process Sources
            </Button>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
