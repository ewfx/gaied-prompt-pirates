"use client";

import { useState, useRef, useEffect, Fragment } from "react";
import axios from "axios";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { UploadCloud } from "lucide-react";
import { motion, animate } from "framer-motion";

const BASE_URL = process.env.REACT_APP_BASE_URL || "http://localhost:8000";

export default function FileUpload() {
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [progress, setProgress] = useState(0);
  const [responseData, setResponseData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [animatedScore, setAnimatedScore] = useState(0);
  const fileInputRef = useRef(null);
  const ignoreKeys=["request_type","sub_request_type","confidence_score"]
  useEffect(() => {
    const confidenceScore =
      responseData?.confidence_score != null
        ? responseData.confidence_score
        : 0;
    animate(0, confidenceScore * 100, {
      duration: 1.5,
      onUpdate: (v) => setAnimatedScore(v),
    });
  }, [responseData]);

  const formatKey = (key) => {
    return key
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };
  const formatKey1 = (key) => {
    if (!key){
      return "N/A"
    }
    return key
      .split(" ")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
    setProgress(0);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    setDragging(true);
  };

  const handleDragLeave = () => {
    setDragging(false);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setDragging(false);
    if (event.dataTransfer.files.length > 0) {
      setFile(event.dataTransfer.files[0]);
      setProgress(0);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);
    setLoading(true);

    try {
      setProgress(0);
      const response = await axios.post(`${BASE_URL}/classify`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setProgress(percentCompleted);
        },
      });
      console.log(response.data.response)
      setResponseData(response.data.response || {});
    } catch (error) {
      console.error("Error uploading file:", error);
      setResponseData({});
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Left Half - File Upload */}
      <div className="w-1/2 flex items-center justify-center">
        <Card className="w-96 p-6 text-center shadow-lg rounded-2xl bg-white">
          <CardContent>
            <div
              className={`flex flex-col items-center p-6 border-2 border-dashed rounded-lg cursor-pointer ${
                dragging ? "bg-gray-200" : "hover:bg-gray-50"
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <UploadCloud className="w-12 h-12 text-gray-500" />
              <span className="mt-2 text-sm text-gray-700">
                Drag & drop a file or click to upload
              </span>
              <input
                type="file"
                className="hidden"
                onChange={handleFileChange}
                ref={fileInputRef}
              />
            </div>
            <Button
              className="mt-4 w-full"
              onClick={() => fileInputRef.current?.click()}
            >
              Choose File
            </Button>
            {file && (
              <p className="mt-4 text-gray-700">Selected: {file.name}</p>
            )}
            {progress > 0 && (
              <div className="mt-4 w-full bg-gray-200 rounded-full h-2.5">
                <div
                  className="bg-blue-600 h-2.5 rounded-full"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
            )}
            <Button
              className="mt-4 w-full"
              onClick={handleUpload}
              disabled={!file || loading}
            >
              {loading ? "Uploading..." : "Upload File"}
            </Button>
            {loading && (
              <p className="mt-2 text-blue-500">
                Uploading file, please wait...
              </p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Right Half - JSON Response Display */}
      <div className="w-1/2 flex items-center justify-center p-6">
        <Card className="w-96 p-6 text-left shadow-lg rounded-2xl bg-white max-h-[500px] overflow-y-auto">
          <CardContent>
            <h2 className="text-lg font-semibold mb-4">Response Details</h2>
            {loading ? (
              <p className="text-gray-500">Loading response...</p>
            ) : (
                <Fragment>
                   <p>
                  <strong>Request Type:</strong>{" "}
                  {responseData?formatKey1(responseData?.request_type) : "N/A"}
                </p>
                <p>
                  <strong>Sub Request Type:</strong>{" "}
                  {responseData?formatKey1(responseData?.sub_request_type) : "N/A"}
                </p>
                <p>
                  <strong>Confidence Score:</strong>{" "}
                  {responseData?.confidence_score != null
                    ? responseData.confidence_score
                    : "N/A"}
                </p>
                <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
                  <motion.div
                    className="bg-green-500 h-2.5 rounded-full"
                    initial={{ width: "0%" }}
                    animate={{ width: `${animatedScore}%` }}
                    transition={{ duration: 1.5 }}
                  ></motion.div>
                </div>
                <div className="text-sm text-gray-700 space-y-2">
                <h3 className="text-lg font-semibold mt-4">Key extracted values:</h3>
                  {responseData && Object.entries(responseData)
                  .filter(([key]) => !ignoreKeys.includes(key))
                  .map(([key, value]) => (
                    <p key={key}><strong>{formatKey(key)}:</strong> {value ?? "N/A"}</p>
                ))}
                </div>
                </Fragment>
              
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
