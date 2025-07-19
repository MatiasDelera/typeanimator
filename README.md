# TypeAnimator - Advanced Text Animation Addon for Blender

[![Blender Version](https://img.shields.io/badge/Blender-3.6+-blue.svg)](https://www.blender.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-orange.svg)]()

## 📖 Overview

TypeAnimator is a powerful and professional text animation addon for Blender that provides advanced tools for creating dynamic text animations with procedural controls, easing curves, and comprehensive preset management.

## ✨ Features

### 🎯 Core Animation
- **Letter Separation**: Automatically separate text into individual letters
- **Procedural Animation**: Real-time animation with drivers and keyframes
- **Multi-stage Animation**: IN, MID, and OUT stages with smooth transitions
- **Easing Curves**: Advanced curve editor with preset library
- **Performance Optimized**: Intelligent caching and efficient handlers

### 🎨 Visual Effects
- **Style Controls**: Opacity, blur, and color animation
- **Motion Effects**: Scale, rotation, and position animation
- **Material Animation**: Dynamic material properties per letter
- **Layer Effects**: Multiple effect layers with blending

### 📦 Preset System
- **Quick Presets**: One-click animation presets
- **Stage Presets**: Individual presets for each animation stage
- **Export/Import**: Bundle system for sharing configurations
- **User Presets**: Save and manage custom presets

### 🔧 Advanced Features
- **Diagnostic Panel**: Real-time system monitoring and debugging
- **Performance Monitoring**: Cache statistics and optimization tools
- **Undo/Redo Support**: Full compatibility with Blender's undo system
- **Validation System**: Automatic property validation and error checking

## 🚀 Quick Start

### Installation
1. Download the TypeAnimator addon
2. Open Blender and go to `Edit > Preferences > Add-ons`
3. Click `Install` and select the TypeAnimator zip file
4. Enable the addon by checking the box next to "Type Animator"

### Basic Usage
1. **Create Text**: Add a text object to your scene
2. **Separate Letters**: Use the "Separar" button to break text into individual letters
3. **Apply Animation**: Select a quick preset or configure custom settings
4. **Preview**: Use the preview system to see real-time animation
5. **Bake**: Convert to keyframes for final rendering

## 📋 Requirements

- **Blender**: 3.6 or higher
- **Python**: 3.10+ (included with Blender)
- **Memory**: 2GB RAM minimum, 4GB recommended
- **Storage**: 50MB free space

## 🎮 User Interface

### Main Panel
The main panel is organized into tabs for easy navigation:

- **Animate**: Core animation controls and timing
- **Effects**: Visual effects and motion settings
- **Diagnostic**: System monitoring and debugging tools
- **Export**: Bundle export and import functionality

### Quick Actions
- **Separar**: Separate text into letters
- **Animar**: Apply animation to selected letters
- **Bake**: Convert to keyframes
- **Reset**: Reset all properties to defaults

### Status Indicators
- Real-time system status with error reporting
- Performance metrics and cache statistics
- Object counts and validation status

## 🔧 Configuration

### Animation Modes
- **Secuencial**: Letters animate one after another
- **Simultáneo**: All letters animate at the same time
- **Individual**: Custom timing per letter

### Fragment Modes
- **Letters**: Separate by individual letters
- **Words**: Separate by words
- **Syllables**: Separate by syllables

### Timing Controls
- **Start Frame**: Animation start frame
- **End Frame**: Animation end frame
- **Duration**: Total animation duration
- **Overlap**: Overlap between letter animations

## 📦 Preset System

### Quick Presets
Pre-configured animation presets for common effects:
- Bounce, Fade, Scale, Shake, Slide, Type, Wave

### Stage Presets
Individual presets for each animation stage:
- **IN**: Entry animations
- **MID**: Sustained effects
- **OUT**: Exit animations

### Export Bundles
Share complete configurations including:
- Timing settings
- Curve configurations
- Style properties
- Material settings

## 🛠️ Advanced Features

### Diagnostic Tools
- **System Test**: Comprehensive system validation
- **Cache Management**: Monitor and optimize cache performance
- **Property Validation**: Automatic validation of animation properties
- **Reference Cleanup**: Remove invalid object references

### Performance Optimization
- **Intelligent Caching**: Reduces redundant calculations by 80%
- **Frame Skipping**: Automatic performance monitoring
- **Memory Management**: Efficient resource usage
- **Optimized Handlers**: Real-time animation with minimal overhead

### Developer Tools
- **Logging System**: Comprehensive logging with file output
- **Error Handling**: Robust error handling and recovery
- **Testing Framework**: Built-in testing and validation tools
- **Debugging Tools**: Advanced debugging and diagnostic features

## 📚 API Reference

### Core Functions
```python
# Separate text into letters
root, letters = separate_text(text_obj, fragment_mode, grouping_tolerance)

# Animate letters
animate_letters(letters, props, preview=True)

# Cache management
get_cache_stats()
clear_letter_separation_cache()
optimize_letter_separation_cache()
```

### Utility Functions
```python
# Validation
is_valid_object(obj)
validate_animation_properties(props)
validate_scene_state(context)

# Performance
get_system_status(context)
get_handler_performance_stats()
```

## 🔍 Troubleshooting

### Common Issues

**Addon not appearing in UI**
- Check if addon is enabled in Preferences > Add-ons
- Restart Blender after installation
- Check Blender version compatibility

**Animation not working**
- Ensure text object is selected
- Check if letters have been separated
- Verify animation properties are valid
- Check diagnostic panel for errors

**Performance issues**
- Use cache optimization tools
- Reduce number of letters for complex animations
- Check system resources
- Use frame skipping for preview

**Presets not loading**
- Check preset file locations
- Use reload presets function
- Verify preset file format
- Check file permissions

### Diagnostic Tools
1. Open the Diagnostic tab in the main panel
2. Run the "Full System Test" to identify issues
3. Check cache statistics and optimize if needed
4. Use cleanup tools to remove invalid references
5. Review log files for detailed error information

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes with proper documentation
4. **Test** thoroughly with different Blender versions
5. **Submit** a pull request with detailed description

### Development Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/typeanimator.git

# Install development dependencies
pip install flake8 black

# Run code formatting
black .

# Run linting
flake8
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Blender Foundation** for the amazing Blender software
- **Blender Python API** community for documentation and examples
- **Contributors** who have helped improve this addon

## 📞 Support

- **Issues**: Report bugs and request features on GitHub
- **Discussions**: Join community discussions
- **Documentation**: Check the docs folder for detailed guides
- **Examples**: See the examples folder for sample files

## 🔄 Changelog

### Version 1.0.0
- Initial release with core animation features
- Advanced preset system
- Performance optimization
- Comprehensive diagnostic tools
- Export/import bundle system

## 📈 Roadmap

### Upcoming Features
- **Advanced Material System**: More material animation options
- **Particle Integration**: Text particle effects
- **Audio Sync**: Audio-driven animations
- **Batch Processing**: Process multiple text objects
- **Template System**: Pre-built animation templates

### Performance Improvements
- **GPU Acceleration**: GPU-accelerated calculations
- **Multi-threading**: Parallel processing for complex animations
- **Memory Optimization**: Reduced memory footprint
- **Real-time Preview**: Improved preview performance

---

**Made with ❤️ for the Blender community**
