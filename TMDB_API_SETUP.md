# TMDb API Configuration

## Overview

The movie recommendation system can fetch movie posters from The Movie Database (TMDb) API. This is optional and the system works perfectly without it.

## Current Status

By default, TMDb API calls are **DISABLED** to prevent timeout errors and ensure smooth operation during development.

## Enable TMDb API (Optional)

If you want to fetch real movie posters, follow these steps:

### 1. Get TMDb API Key

1. Go to [https://www.themoviedb.org/](https://www.themoviedb.org/)
2. Create a free account
3. Go to Settings → API
4. Request an API key (it's free)

### 2. Enable API in Your Environment

Set environment variables in your system:

**Windows (PowerShell):**
```powershell
$env:TMDB_API_ENABLED="true"
$env:TMDB_API_KEY="your-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set TMDB_API_ENABLED=true
set TMDB_API_KEY=your-api-key-here
```

**Linux/Mac:**
```bash
export TMDB_API_ENABLED=true
export TMDB_API_KEY=your-api-key-here
```

### 3. Restart Django Server

```bash
python manage.py runserver
```

## Alternative: Manual Poster Setup

Instead of using the API, you can set up sample posters manually:

```bash
python manage.py setup_sample_posters
```

This command will add poster URLs for popular movies without making API calls.

## Troubleshooting

### API Timeout Errors

If you see timeout errors like:
```
ConnectTimeoutError: Connection to api.themoviedb.org timed out
```

**Solution**: Disable the API temporarily:
```bash
# Windows
$env:TMDB_API_ENABLED="false"

# Linux/Mac  
export TMDB_API_ENABLED=false
```

### No Posters Showing

1. **Check API Status**: Ensure `TMDB_API_ENABLED=true` if you want API posters
2. **Run Sample Setup**: `python manage.py setup_sample_posters`
3. **Check Network**: Ensure you can access themoviedb.org
4. **Verify API Key**: Make sure your TMDb API key is correct

## System Behavior

### With API Enabled
- ✅ Fetches real movie posters from TMDb
- ✅ Caches poster URLs in database
- ⚠️ May experience timeouts if TMDb is slow

### With API Disabled (Default)
- ✅ No network calls or timeouts
- ✅ Uses cached poster URLs if available
- ✅ Shows placeholder icons for movies without posters
- ✅ Faster page loads

## Recommendation

For **development and testing**: Keep API disabled (default)
For **production**: Enable API with proper error handling

The recommendation system works perfectly either way! 🎬
