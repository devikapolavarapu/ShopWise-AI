import React, { useState, useRef } from 'react';
import { scanProductImage } from '../services/api';
import { ProductScanResponse } from '../types';
import { Camera, ShieldCheck, AlertTriangle, Upload, CheckCircle2, FileText, Sparkles, Image as ImageIcon, RotateCcw } from 'lucide-react';

export const ProductScanModal: React.FC = () => {
  const [targetProduct, setTargetProduct] = useState("Amul Milk");
  const [scanResult, setScanResult] = useState<ProductScanResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedPreset, setSelectedPreset] = useState<string | null>("fresh_milk");
  const [uploadedImagePreview, setUploadedImagePreview] = useState<string | null>(null);
  const [uploadedBase64, setUploadedBase64] = useState<string | null>(null);
  const [scanError, setScanError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Preset Scan Handler
  const handlePresetScan = async (presetKey: string) => {
    setSelectedPreset(presetKey);
    setUploadedImagePreview(null);
    setUploadedBase64(null);
    setScanError(null);
    setIsLoading(true);
    try {
      const res = await scanProductImage(presetKey, undefined, targetProduct);
      setScanResult(res);
    } catch (e: any) {
      console.error(e);
      setScanError(e.message || "OCR scan request failed. Please check backend connection.");
    } finally {
      setIsLoading(false);
    }
  };

  // Image File Upload Handler
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      setScanError("Please select a valid image file (JPG, PNG, WebP).");
      return;
    }

    setScanError(null);
    setSelectedPreset(null);

    const reader = new FileReader();
    reader.onload = () => {
      const base64Str = reader.result as string;
      setUploadedImagePreview(base64Str);
      setUploadedBase64(base64Str);
    };
    reader.readAsDataURL(file);
  };

  // Run Custom OCR Upload Scan
  const handleUploadScan = async () => {
    if (!uploadedBase64) {
      setScanError("Please upload a product label image first.");
      return;
    }

    setIsLoading(true);
    setScanError(null);
    try {
      const res = await scanProductImage(undefined, uploadedBase64, targetProduct);
      setScanResult(res);
      if (res.error) {
        setScanError(res.error);
      }
    } catch (e: any) {
      console.error(e);
      setScanError(e.message || "OCR image scan failed. Ensure backend OCR engine is active.");
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'FRESH':
        return <span className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-3 py-1 rounded-full font-bold text-sm flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4" /> 🟢 FRESH (Good to Buy)</span>;
      case 'GOOD':
        return <span className="bg-blue-500/20 text-blue-400 border border-blue-500/30 px-3 py-1 rounded-full font-bold text-sm flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4" /> 🔵 GOOD</span>;
      case 'USE_SOON':
        return <span className="bg-amber-500/20 text-amber-400 border border-amber-500/30 px-3 py-1 rounded-full font-bold text-sm flex items-center gap-1.5"><AlertTriangle className="w-4 h-4" /> ⚠️ USE SOON</span>;
      case 'NEAR_EXPIRY':
        return <span className="bg-orange-500/20 text-orange-400 border border-orange-500/30 px-3 py-1 rounded-full font-bold text-sm flex items-center gap-1.5"><AlertTriangle className="w-4 h-4" /> 🟠 NEAR EXPIRY</span>;
      case 'EXPIRED':
        return <span className="bg-rose-500/20 text-rose-400 border border-rose-500/30 px-3 py-1 rounded-full font-bold text-sm flex items-center gap-1.5"><AlertTriangle className="w-4 h-4" /> 🔴 EXPIRED (Do Not Purchase)</span>;
      default:
        return <span className="bg-purple-500/20 text-purple-400 border border-purple-500/30 px-3 py-1 rounded-full font-bold text-sm flex items-center gap-1.5"><AlertTriangle className="w-4 h-4" /> ❓ UNVERIFIED</span>;
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 p-4">
      {/* Header Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 text-center space-y-2 shadow-lg">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 mb-2">
          <Camera className="w-6 h-6" />
        </div>
        <h2 className="text-2xl font-bold text-white font-outfit">Product Scan & OCR Verification</h2>
        <p className="text-sm text-slate-400 max-w-xl mx-auto">
          Upload a product label image or select a preset. ShopWise runs Tesseract OCR date extraction, computes deterministic shelf life %, and verifies product identity.
        </p>
      </div>

      {/* Target Product Input */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-4">
        <div>
          <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">Target Product Name</label>
          <input
            type="text"
            value={targetProduct}
            onChange={(e) => setTargetProduct(e.target.value)}
            className="w-full py-2.5 px-4 bg-slate-950 text-white rounded-xl border border-slate-800 text-sm focus:outline-none focus:border-emerald-500 font-medium"
            placeholder="e.g. Amul Milk"
          />
        </div>

        {/* SECTION A: UPLOAD PRODUCT LABEL IMAGE */}
        <div className="border-t border-slate-800/80 pt-4 space-y-3">
          <span className="block text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5 font-outfit">
            <Upload className="w-4 h-4 text-emerald-400" /> Option 1: Upload Product Label Image
          </span>

          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept="image/*"
            className="hidden"
          />

          <div className="flex flex-col sm:flex-row items-center gap-4">
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="w-full sm:w-auto px-5 py-3 bg-slate-950 hover:bg-slate-800 text-slate-200 border border-dashed border-slate-700 hover:border-emerald-500 rounded-xl text-xs font-bold transition flex items-center justify-center gap-2"
            >
              <ImageIcon className="w-4 h-4 text-emerald-400" />
              <span>{uploadedImagePreview ? "Choose Different Image" : "Select Label Image File"}</span>
            </button>

            {uploadedImagePreview && (
              <div className="flex items-center gap-3 w-full sm:w-auto">
                <img
                  src={uploadedImagePreview}
                  alt="Label Preview"
                  className="w-14 h-14 object-cover rounded-xl border border-slate-700 bg-slate-950"
                />
                <button
                  type="button"
                  disabled={isLoading}
                  onClick={handleUploadScan}
                  className="px-5 py-3 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-extrabold rounded-xl text-xs transition flex items-center gap-2 shadow-lg disabled:opacity-50"
                >
                  <Camera className="w-4 h-4" />
                  <span>Run OCR & Verify Product</span>
                </button>
              </div>
            )}
          </div>
        </div>

        {/* SECTION B: TRY DEMO PRESET LABELS */}
        <div className="border-t border-slate-800/80 pt-4 space-y-3">
          <span className="block text-xs font-bold text-slate-400 uppercase tracking-wider font-outfit">
            Option 2: Try Demo Label Presets
          </span>
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
            <button
              type="button"
              onClick={() => handlePresetScan('fresh_milk')}
              className={`p-3 rounded-xl border text-left text-xs font-semibold transition-all ${
                selectedPreset === 'fresh_milk'
                  ? 'bg-emerald-500/10 border-emerald-500 text-emerald-300'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              🥛 Fresh Amul Milk (82% Shelf Life)
            </button>

            <button
              type="button"
              onClick={() => handlePresetScan('near_expiry_milk')}
              className={`p-3 rounded-xl border text-left text-xs font-semibold transition-all ${
                selectedPreset === 'near_expiry_milk'
                  ? 'bg-amber-500/10 border-amber-500 text-amber-300'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              ⚠️ Near Expiry Milk (1 Day Left)
            </button>

            <button
              type="button"
              onClick={() => handlePresetScan('expired_product')}
              className={`p-3 rounded-xl border text-left text-xs font-semibold transition-all ${
                selectedPreset === 'expired_product'
                  ? 'bg-rose-500/10 border-rose-500 text-rose-300'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              🔴 Expired Britannia Bread
            </button>

            <button
              type="button"
              onClick={() => handlePresetScan('ocr_failed')}
              className={`p-3 rounded-xl border text-left text-xs font-semibold transition-all ${
                selectedPreset === 'ocr_failed'
                  ? 'bg-purple-500/10 border-purple-500 text-purple-300'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              📷 Blurry OCR Failure Test
            </button>
          </div>
        </div>
      </div>

      {/* ERROR DISPLAY */}
      {scanError && (
        <div className="bg-rose-500/10 border border-rose-500/30 p-4 rounded-2xl flex items-center gap-3 text-rose-300 text-sm">
          <AlertTriangle className="w-5 h-5 shrink-0" />
          <span>{scanError}</span>
        </div>
      )}

      {/* VERIFICATION RESULTS */}
      {isLoading ? (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center space-y-3">
          <div className="w-8 h-8 border-3 border-emerald-400 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-sm font-semibold text-slate-300">Running Tesseract OCR date extraction & calculating shelf life...</p>
        </div>
      ) : scanResult ? (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            
            {/* Freshness Status Card */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-md">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase text-slate-400 tracking-wider">Deterministic Freshness</span>
                {getStatusBadge(scanResult.freshness.status)}
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-xs text-slate-400 font-medium">
                  <span>Shelf Life Remaining</span>
                  <span className="text-white font-bold">{scanResult.freshness.freshness_percentage}%</span>
                </div>
                <div className="w-full bg-slate-950 h-3 rounded-full overflow-hidden p-0.5 border border-slate-800">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      scanResult.freshness.freshness_percentage > 70
                        ? 'bg-gradient-to-r from-emerald-500 to-teal-400'
                        : scanResult.freshness.freshness_percentage > 30
                        ? 'bg-gradient-to-r from-amber-500 to-yellow-400'
                        : 'bg-gradient-to-r from-rose-500 to-red-400'
                    }`}
                    style={{ width: `${scanResult.freshness.freshness_percentage}%` }}
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-2 text-center text-xs bg-slate-950 p-3 rounded-xl border border-slate-800">
                <div>
                  <span className="text-slate-500 block uppercase font-bold text-[10px]">MFD</span>
                  <strong className="text-slate-200 font-mono">{scanResult.detected_mfd || 'N/A'}</strong>
                </div>
                <div>
                  <span className="text-slate-500 block uppercase font-bold text-[10px]">EXP</span>
                  <strong className="text-emerald-400 font-mono">{scanResult.detected_exp || 'N/A'}</strong>
                </div>
                <div>
                  <span className="text-slate-500 block uppercase font-bold text-[10px]">Batch</span>
                  <strong className="text-slate-200 font-mono">{scanResult.detected_batch || 'N/A'}</strong>
                </div>
              </div>
            </div>

            {/* CV Identity Match Card */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-md">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase text-slate-400 tracking-wider">CV Product Identity Match</span>
                <span className={`px-3 py-1 rounded-full font-bold text-xs ${
                  scanResult.cv_match_status === 'Likely Match'
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                    : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                }`}>
                  {scanResult.cv_match_status} ({Math.round(scanResult.cv_confidence * 100)}%)
                </span>
              </div>

              <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 text-xs space-y-1.5">
                <span className="text-slate-400 font-semibold flex items-center gap-1.5">
                  <FileText className="w-4 h-4 text-cyan-400" /> Extracted OCR Text:
                </span>
                <pre className="text-slate-300 font-mono text-[11px] whitespace-pre-wrap bg-slate-900 p-2.5 rounded border border-slate-800 max-h-32 overflow-y-auto">{scanResult.ocr_text || "(No text extracted)"}</pre>
              </div>
            </div>

          </div>

          {/* Evidence Trail */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 text-xs space-y-2">
            <span className="font-bold text-slate-300 flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-cyan-400" /> Verification Evidence Trail:
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-slate-400">
              {scanResult.evidence.map((ev, i) => (
                <p key={i} className="flex items-start gap-1">
                  <span className="text-emerald-400 font-bold">•</span>
                  <span>{ev}</span>
                </p>
              ))}
            </div>
          </div>

        </div>
      ) : null}
    </div>
  );
};
