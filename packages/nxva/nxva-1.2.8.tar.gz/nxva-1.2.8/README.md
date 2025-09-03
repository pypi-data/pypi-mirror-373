# <div align="center"> NXVA - Nexuni Video Analysis</div>

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.6%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-orange.svg)](pyproject.toml)

**A comprehensive computer vision toolkit for video analysis, object detection, tracking, and pose estimation**

</div>

## Overview

NXVA (Nexuni Video Analysis) is a powerful and versatile Python package designed for advanced video analysis tasks. It provides a unified interface for object detection, multi-object tracking, pose estimation, and real-time streaming capabilities. Built with modularity and ease-of-use in mind, NXVA supports multiple deep learning frameworks and model formats.

## ✨ Key Features

- **Multi-Model Object Detection**: Support for YOLOv5, YOLOv11 with ONNX, PyTorch, and TensorRT formats
- **Advanced Object Tracking**: SimpleTracker and NexuniSort algorithms with feature-based tracking
- **Pose Estimation**: MMPose integration for human pose detection and analysis
- **Multi-Camera Streaming**: Real-time streaming with automatic reconnection and GStreamer support
- **Flexible Configuration**: YAML-based configuration system for easy setup and deployment
- **GPU Acceleration**: Full CUDA and TensorRT support for high-performance inference
- **Model Conversion**: Built-in tools for model format conversion and optimization

## 🏗️ Architecture

```
nxva/
├── v5/          # YOLOv5 detection, classification, pose estimation
├── v11/         # YOLOv11 detection, classification, pose estimation  
├── sort/        # Object tracking algorithms (SimpleTracker, NexuniSort)
├── pose/        # MMPose integration for pose estimation
├── utilities/   # Utility functions and tools
├── streaming/   # Multi-camera streaming capabilities
└── va/          # Video analysis server components
```

## 🚀 Quick Start

### Installation

```bash
pip install nxva
```

### Basic Usage

Each module provides detailed usage instructions and examples:

- **Object Detection**: See [YOLOv11 README](nxva/v11/README.md) and [YOLOv5 README](nxva/v5/README.md) for detection setup and usage
- **Object Tracking**: Refer to [Sort README](nxva/sort/README.md) for SimpleTracker and NexuniSort usage
- **Pose Estimation**: Check [Pose README](nxva/pose/README.md) for MMPose integration guide  
- **Multi-Camera Streaming**: See [Main README](nxva/README.md#streaming) for streaming configuration
- **Complete Examples**: Explore [tutorials/](tutorials/) for Jupyter notebook examples

## 📋 Requirements

### Core Dependencies
- Python 3.6 or higher
- OpenCV 4.6.0+
- PyTorch 1.8.0+ (with CUDA support)
- NumPy 1.23.0+
- PyYAML 5.3.1+

### Optional Dependencies
- **For ONNX models**: ONNX Runtime
- **For TensorRT**: TensorRT 7.0.0+ (not 10.1.0)
- **For Pose Estimation**: MMPose, MMDetection, MMEngine, MMCV
- **For Advanced Features**: ultralytics, torchvision

## 📚 Documentation & Examples

The package includes comprehensive tutorials and examples:

- **Jupyter Notebooks**: Step-by-step tutorials in `tutorials/`
- **Configuration Examples**: Ready-to-use configs in `example/`
- **Specific Use Cases**: Detection, tracking, pose estimation examples
- **Module Documentation**: Detailed README files for each component

### Tutorial Topics
- YOLOv11 Training and Inference
- Multi-Object Tracking with NexuniSort
- Real-time Streaming Setup
- Pose Estimation with MMPose
- Model Conversion and Optimization

## 🎯 Use Cases

- **Security & Surveillance**: Real-time monitoring with object detection and tracking
- **Sports Analysis**: Pose estimation and movement analysis
- **Industrial Automation**: Quality control and process monitoring  
- **Retail Analytics**: Customer behavior analysis and people counting
- **Research & Development**: Computer vision prototyping and experimentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.