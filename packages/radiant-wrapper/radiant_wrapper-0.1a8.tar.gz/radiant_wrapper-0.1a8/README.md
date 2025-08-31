# Radiant-Wrapper

Radiant-Wrapper is a Docker image that allows you to generate APKs for Android. It's essentially a wrapper for [python-for-android](https://python-for-android.readthedocs.io/en/latest/) with all dependencies included. This tool has the ability to compile three kinds of projects:

1. **Static HTML** - Projects with an index.html file
2. **Django Projects** - Web applications built with Django
3. **Python Projects** - Any Python project that implements a main.py file

## Installation

Pull the Docker image that includes the [Android NDK](https://developer.android.com/studio/projects/install-ndk) and [SDK](https://developer.android.com/studio):

```bash
docker pull dunderlab/radiant_p4a
```

Then install the Python package to use the wrapper command:

```bash
pip install radiant-wrapper
```

## Usage

The `radiant_p4a` command replaces the standard `p4a` command and runs it inside the Docker container:

```bash
radiant_p4a.py apk --arch arm64-v8a
```

### Project Types

#### Static HTML

If your project contains an `index.html` file, Radiant-Wrapper will automatically create a main.py file that sets up a
simple HTTP server to serve your static files.  
For a complete example of a static HTML project, see: https://github.com/dunderlab/radiant-html_template

#### Django Projects

If your project contains a Django application (identified by the presence of `manage.py`), Radiant-Wrapper will set up
the necessary environment to run your Django app on Android.  
For a complete example of a Django project, see: https://github.com/dunderlab/radiant-django_template


#### Python Projects with main.py
If your project already has a `main.py` file, Radiant-Wrapper will use it directly to build your Android application.

### GitHub Workflow for Automated APK Generation

A GitHub workflow is available to automate the APK generation process. When added to your repository, this workflow will automatically build an Android APK for your project on every push or when manually triggered. The workflow handles all project types (Static HTML, Django, and Python with main.py) and uploads the generated APK as an artifact.

To use this workflow, copy the `radiant_wrapper.yml` file to your repository's `.github/workflows/` directory.

## Software Versions Included in the Image

```
NDK_VERSION=r25b
SDK_VERSION=10406996_latest
JAVA_VERSION=jdk17-openjdk
NDKAPI=30
ANDROIDAPI=30
BUILDTOOL=34.0.0
P4A_VERSION=2024.1.21
CYTHON_VERSION=3.0.4
```
