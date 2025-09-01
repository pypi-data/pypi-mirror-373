# mpv-yt

A command-line tool to stream YouTube videos with `mpv`.

## Prerequisites

Requires `mpv` media player to be installed and available in your system's PATH.

## Installation

```sh
pip install .
```

## Usage

The tool can be invoked with the `play` command, followed by a YouTube video URL or ID. If no identifier is provided, the tool will prompt for input.

### Interactive Mode

Run the command without a video identifier to be prompted for one. Then, select the desired stream quality from the interactive list.

```sh
play
```

### Direct Playback

Provide a YouTube URL or video ID directly as an argument.

```sh
play "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
# or
play dQw4w9WgXcQ
```

### Quality Selection

Specify a video quality to bypass the interactive selection. The tool supports specific resolutions (e.g., `1080p`, `720p`), `highest`, or `lowest`.

```sh
play dQw4w9WgXcQ --quality 1080p
```

### Audio-Only Mode

Use the `--audio` flag to stream only the audio track.

```sh
play dQw4w9WgXcQ --audio
```

## Options

| Argument              | Short | Description                                                              |
| --------------------- | ----- | ------------------------------------------------------------------------ |
| `identifier`          |       | The YouTube URL or Video ID to play.                                     |
| `--quality <quality>` | `-q`  | Set a preferred quality (e.g., `1080p`, `highest`, `lowest`).            |
| `--audio`             | `-a`  | Play audio only.                                                         |