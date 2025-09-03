#!/bin/bash

# Name of the output file
OUTPUT_FILE="merged_code.txt"

# Clear or create the output file
> "$OUTPUT_FILE"

# List of file extensions to include
extensions=("py" "js" "ts" "jsx" "tsx" "rs" "ex" "exs" "go" "java" "c" "cpp" "h" "hpp" "cs" "rb" "php" "html" "css" "kt" "swift" "scala" "sh" "pl" "r" "lua" "m" "erl" "hs")

# Check if we're in a git repository
if git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    # Use git ls-files to get all tracked files and untracked files not ignored by .gitignore
    # Get specific files and service subdirectories
    files_specific=$(git ls-files --cached --others --exclude-standard -- \
        'src/pipecat/services/ai_service.py' \
        'src/pipecat/services/llm_service.py' \
        'src/pipecat/services/websocket_service.py' \
        'src/pipecat/services/openai.py' \
        'src/pipecat/services/stt_service.py' \
        'src/pipecat/services/tts_service.py' \
        'src/pipecat/services/vision_service.py' \
        'src/pipecat/services/image_service.py' \
        'src/pipecat/services/websocket_service.py' \
        'src/pipecat/services/azure/stt.py' \
        'src/pipecat/services/azure/tts.py' \
        'src/pipecat/services/elevenlabs/tts.py' \
        'src/pipecat/services/deepgram/stt.py' \
        'src/pipecat/services/openai/llm.py' \
        'src/pipecat/services/openai/stt.py' \
        'src/pipecat/services/openai/tts.py' \
        'src/pipecat/services/google/llm.py' \
        'src/pipecat/services/google/llm_openai.py' \
        'src/pipecat/services/google/stt.py' \
        'src/pipecat/services/google/tts.py' \
        'src/pipecat/audio/vad/silero.py' \
        'src/pipecat/audio/vad/vad_analyzer.py' \
        'src/pipecat/clocks/system_clock.py' \
        'src/pipecat/frames/frames.py' \
        'src/pipecat/metrics/metrics.py' \
        'src/pipecat/pipeline/**' \
        'src/pipecat/processors/aggregators/llm_response.py' \
        'src/pipecat/processors/aggregators/openai_llm_context.py' \
        'src/pipecat/processors/aggregators/user_response.py' \
        'src/pipecat/processors/filters/stt_mute_filter.py' \
        'src/pipecat/processors/filters/function_filter.py' \
        'src/pipecat/processors/dtmf_aggregator.py' \
        'src/pipecat/processors/frame_processor.py' \
        'src/pipecat/processors/idle_frame_processor.py' \
        'src/pipecat/processors/transcript_processor.py' \
        'src/pipecat/processors/user_idle_processor.py' \
        'src/pipecat/processors/two_stage_user_idle_processor.py' \
        'src/pipecat/serializers/plivo.py' \
        'src/pipecat/serializers/exotel.py' \
        'src/pipecat/utils/**'
    )

    # Get all files under src/pipecat, excluding certain subdirectories and all of services/
    # files_general=$(git ls-files --cached --others --exclude-standard -- \
    #     'src/pipecat' \
    #     ':!src/pipecat/processors/frameworks/**' \
    #     ':!src/pipecat/processors/gstreamer/**' \
    #     ':!src/pipecat/processors/transports/services/**' \
    #     ':!src/pipecat/processors/tests/**' \
    #     ':!src/pipecat/services/**' \
    #     ':!src/pipecat/audio/mixers/**' \
    #     ':!src/pipecat/audio/filters/**'
    # )

    # Combine the results
    files="$files_specific"$'\n'"$files_general"
else
    # If not in a git repository, fall back to find
    files=$(find . -type f)
fi

# Iterate through all files
echo "$files" | while read -r file; do
    # Get the file extension
    extension="${file##*.}"

    # Check if the file extension is in our list
    if [[ " ${extensions[*]} " == *" $extension "* ]]; then
        # Check if the file is empty
        if [ ! -s "$file" ]; then
            echo "Skipping empty file: $file"
            continue  # Skip to the next file
        fi
        # Write the filename to the output file
        echo "File: $file" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"

        # Append the file content to the output file
        grep -vE "(Copyright|SPDX-License-Identifier|^#$)" "$file" >> "$OUTPUT_FILE"

        # Add a separator between files
        echo -e "\n\n--- End of $file ---\n\n" >> "$OUTPUT_FILE"
    fi
done