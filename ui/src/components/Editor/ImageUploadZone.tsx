import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload } from 'lucide-react';
import { useEditorStore } from '../../stores/editorStore';

export function ImageUploadZone() {
  const setFile = useEditorStore((state) => state.setFile);
  const setFileUrl = useEditorStore((state) => state.setFileUrl);
  const setFileSource = useEditorStore((state) => state.setFileSource);
  const setImageDimensions = useEditorStore((state) => state.setImageDimensions);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setFile(file);
    setFileSource('upload');

    // Create preview URL
    const url = URL.createObjectURL(file);
    setFileUrl(url);

    // Get dimensions for images
    if (file.type.startsWith('image/')) {
      const img = new Image();
      img.onload = () => {
        setImageDimensions({
          width: img.naturalWidth,
          height: img.naturalHeight,
        });
      };
      img.src = url;
    } else if (file.type.startsWith('video/')) {
      // Get video dimensions
      const video = document.createElement('video');
      video.onloadedmetadata = () => {
        setImageDimensions({
          width: video.videoWidth,
          height: video.videoHeight,
        });
      };
      video.src = url;
    }
  }, [setFile, setFileUrl, setFileSource, setImageDimensions]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpg', '.jpeg', '.png'],
      'video/*': ['.mp4', '.mov', '.avi'],
    },
    maxFiles: 1,
  });

  return (
    <div
      {...getRootProps()}
      className={`
        border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
        transition-colors duration-200
        ${
          isDragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }
      `}
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center space-y-4">
        <Upload className="w-16 h-16 text-gray-400" />
        {isDragActive ? (
          <p className="text-lg font-medium text-blue-600">Drop the file here...</p>
        ) : (
          <div>
            <p className="text-lg font-medium text-gray-700 mb-2">
              Drag & drop an image or video
            </p>
            <p className="text-sm text-gray-500">or click to select</p>
            <p className="text-xs text-gray-400 mt-2">
              Supports JPG, PNG, MP4, MOV, AVI
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
