"use client"

import { useState, useEffect } from "react";
import { BreadcrumbType } from "@/types";
import { AppHeader } from "@/components/main/app-header";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { predictHousePrice, triggerTrainingModel, fetchTrainingStatus } from "@/services/model";
import { TrainingStatus, PredictRequest } from "@/types";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import Heading from "@/components/ui/heading";

interface PredictionHistoryItem extends PredictRequest {
  id: string;
  timestamp: string;
  predicted_price: number;
}

const STORAGE_KEY_HISTORY = "homeiq_prediction_history";
const STORAGE_KEY_STATUS = "homeiq_training_status";
const TWENTY_FOUR_HOURS = 24 * 60 * 60 * 1000;

// Helper untuk menyimpan data dengan timestamp
const saveWithExpiry = (key: string, value: any) => {
  const item = {
    value: value,
    timestamp: new Date().getTime(),
  };
  localStorage.setItem(key, JSON.stringify(item));
};

// Helper untuk mengambil data dan cek expiry
const getWithExpiry = (key: string) => {
  const itemStr = localStorage.getItem(key);
  if (!itemStr) return null;

  const item = JSON.parse(itemStr);
  const now = new Date().getTime();

  // Jika data lebih lama dari 24 jam, hapus dan kembalikan null
  if (now - item.timestamp > TWENTY_FOUR_HOURS) {
    localStorage.removeItem(key);
    return null;
  }
  return item.value;
};

export default function Page() {
  const breadcrumbs: BreadcrumbType[] = [
    { label: "HomeIQ", href: "/" },
    { label: "Model", href: "/model" },
  ];

  const CITY_DISTRICT_MAP: Record<string, string[]> = {
    "Kota Bekasi": [
      "Mustikajaya (Mustika Jaya)", "Medansatria (Medan Satria)", "Bekasi Barat",
      "Rawalumbu", "Pondokgede (Pondok Gede)", "Bekasi Timur", "Jatiasih",
      "Jatisampurna (Jati Sampurna)", "Pondokmelati (Pondok Melati)", "Bekasi Utara",
      "Bekasi Selatan", "Bantargebang (Bantar Gebang)"
    ],
    "Kota Bogor": [
      "Bogor Utara", "Bogor Selatan", "Bogor Barat", "Tanah Sareal (Tanah Sereal)",
      "Bogor Timur", "Bogor Tengah", "Gunung Sindur"
    ],
    "Kota Depok": [
      "Sawangan", "Cinere", "Cipayung", "Bojongsari", "Limo", "Cimanggis",
      "Pancoran Mas", "Beji", "Cilodong", "Sukmajaya", "Tapos"
    ],
    "Kota Jakarta Barat": [
      "Kembangan", "Grogol Petamburan", "Kalideres", "Kebon Jeruk", "Cengkareng",
      "Taman Sari", "Pal Merah (Palmerah)", "Tambora"
    ],
    "Kota Jakarta Pusat": [
      "Sawah Besar", "Cempaka Putih", "Johar Baru", "Gambir", "Kemayoran",
      "Menteng", "Tanah Abang", "Senen"
    ],
    "Kota Jakarta Selatan": [
      "Kebayoran Lama", "Jagakarsa", "Pasar Minggu", "Setiabudi (Setia Budi)",
      "Cilandak", "Pesanggrahan", "Mampang Prapatan", "Kebayoran Baru", "Tebet", "Pancoran"
    ],
    "Kota Jakarta Timur": [
      "Ciracas", "Pasar Rebo", "Cakung", "Duren Sawit", "Kramatjati (Kramat Jati)",
      "Pulogadung (Pulo Gadung)", "Matraman", "Makasar", "Jatinegara"
    ],
    "Kota Jakarta Utara": [
      "Tanjung Priok", "Kelapa Gading", "Pademangan", "Cilincing", "Penjaringan", "Koja"
    ],
    "Kota Tangerang": [
      "Karang Tengah", "Cibodas", "Pinang (Penang)", "Cipondoh", "Tangerang",
      "Karawaci", "Ciledug", "Larangan", "Benda", "Periuk", "Neglasari", "Batuceper", "Jatiuwung"
    ],
  };

  const [predictForm, setPredictForm] = useState({
    bedrooms: 0,
    bathrooms: 0,
    building_size_m2: 0,
    land_size_m2: 0,
    city: "",
    district: "",
  });
  const [predictionResult, setPredictionResult] = useState<number | null>(null);
  const [isPredicting, setIsPredicting] = useState(false);
  const [predictError, setPredictError] = useState<string | null>(null);
  const [history, setHistory] = useState<PredictionHistoryItem[]>([]);
  const [trainingStatus, setTrainingStatus] = useState<TrainingStatus | null>(null);
  const [isTrainingLoading, setIsTrainingLoading] = useState(false);
  const [trainMessage, setTrainMessage] = useState<string | null>(null);

  const checkStatus = async () => {
    try {
      const status = await fetchTrainingStatus();
      setTrainingStatus(status);
      saveWithExpiry(STORAGE_KEY_STATUS, status); // Simpan ke local
    } catch (error: any) {
      console.error("Gagal mengambil status:", error);
    }
  };

  useEffect(() => {
    const savedHistory = getWithExpiry(STORAGE_KEY_HISTORY);
    if (savedHistory) setHistory(savedHistory);

    const savedStatus = getWithExpiry(STORAGE_KEY_STATUS);
    if (savedStatus) {
      setTrainingStatus(savedStatus);
    } else {
      void checkStatus(); // Jika tidak ada di local, baru fetch ke server
    }
  }, []);

  const handleSelectChange = (name: string, value: string) => {
    setPredictForm((prev) => {
      const newData = { ...prev, [name]: value };
      if (name === "city") {
        newData.district = "";
      }
      return newData;
    });
  };

  const handlePredictChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setPredictForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handlePredictSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsPredicting(true);
    setPredictError(null);

    const payload: PredictRequest = {
      bedrooms: Number(predictForm.bedrooms),
      bathrooms: Number(predictForm.bathrooms),
      building_size_m2: Number(predictForm.building_size_m2),
      land_size_m2: Number(predictForm.land_size_m2),
      city: predictForm.city,
      district: predictForm.district,
    };

    try {
      const res = await predictHousePrice(payload);
      setPredictionResult(res.predicted_price);

      const newHistoryItem: PredictionHistoryItem = {
        ...payload,
        id: Math.random().toString(36).substring(7),
        timestamp: new Date().toLocaleString("id-ID"),
        predicted_price: res.predicted_price,
      };

      const updatedHistory = [newHistoryItem, ...history];
      setHistory(updatedHistory);
      saveWithExpiry(STORAGE_KEY_HISTORY, updatedHistory); // Simpan ke local

    } catch (error: any) {
      setPredictError(error?.response?.data?.detail || "Gagal melakukan prediksi.");
    } finally {
      setIsPredicting(false);
    }
  };

  const handleTrainModel = async () => {
    setIsTrainingLoading(true);
    setTrainMessage(null);
    try {
      const res = await triggerTrainingModel();
      setTrainMessage(res.message);

      // Update status lokal menjadi RUNNING segera agar UI responsif
      const runningStatus: TrainingStatus = { status: "RUNNING" };
      setTrainingStatus(runningStatus);
      saveWithExpiry(STORAGE_KEY_STATUS, runningStatus);

      await checkStatus();
    } catch (error: any) {
      setTrainMessage(error?.response?.data?.detail || "Gagal memicu proses training.");
    } finally {
      setIsTrainingLoading(false);
    }
  };

  return (
    <>
      <AppHeader breadcrumbs={breadcrumbs} />
      <div className="flex flex-1 flex-col gap-6 p-4 pt-2 w-full mx-auto">
        <Heading title="Model" description="Prediksi harga rumah dan training model." />
        <Tabs defaultValue="predict" className="w-full">
          <TabsList className="grid w-full grid-cols-3 h-20 p-1 bg-muted">
            <TabsTrigger
              value="predict"
              className="py-1.5 text-sm font-medium transition-all"
            >
              <span>Prediksi</span>
              <span className="hidden sm:block">Harga</span>
            </TabsTrigger>
            <TabsTrigger
              value="train"
              className="py-1.5 text-sm font-medium transition-all"
            >
              <span>Training</span>
              <span className="hidden sm:block">Model</span>
            </TabsTrigger>
            <TabsTrigger
              value="history"
              className="py-1.5 text-sm font-medium transition-all"
            >
              <span>Riwayat</span>
              <span className="hidden sm:block">& Status</span>
            </TabsTrigger>
          </TabsList>

          {/* TAB 1: PREDIKSI */}
          <TabsContent value="predict" className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle>Prediksi Harga Properti</CardTitle>
                <CardDescription>Masukkan spesifikasi rumah untuk estimasi harga.</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handlePredictSubmit} suppressHydrationWarning className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="bedrooms">Kamar Tidur</Label>
                    <Input 
                      id="bedrooms" 
                      name="bedrooms" 
                      type="number" 
                      required 
                      value={predictForm.bedrooms} 
                      onChange={handlePredictChange}
                      suppressHydrationWarning
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="bathrooms">Kamar Mandi</Label>
                    <Input 
                      id="bathrooms" 
                      name="bathrooms" 
                      type="number" 
                      required 
                      value={predictForm.bathrooms} 
                      onChange={handlePredictChange}
                      suppressHydrationWarning
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="building_size_m2">Luas Bangunan (m²)</Label>
                    <Input 
                      id="building_size_m2" 
                      name="building_size_m2" 
                      type="number" 
                      required 
                      value={predictForm.building_size_m2} 
                      onChange={handlePredictChange}
                      suppressHydrationWarning
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="land_size_m2">Luas Tanah (m²)</Label>
                    <Input 
                      id="land_size_m2" 
                      name="land_size_m2" 
                      type="number" 
                      required 
                      value={predictForm.land_size_m2} 
                      onChange={handlePredictChange}
                      suppressHydrationWarning
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="city">Kota</Label>
                    <Select
                      value={predictForm.city}
                      onValueChange={(val) => handleSelectChange("city", val)}
                    >
                      <SelectTrigger className="h-12 w-full">
                        <SelectValue placeholder="Pilih Kota" />
                      </SelectTrigger>
                      <SelectContent>
                        {Object.keys(CITY_DISTRICT_MAP).map((city) => (
                          <SelectItem key={city} value={city}>{city}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="district">Kecamatan</Label>
                    <Select
                      value={predictForm.district}
                      onValueChange={(val) => handleSelectChange("district", val)}
                      disabled={!predictForm.city}
                    >
                      <SelectTrigger className="h-12 w-full" suppressHydrationWarning>
                        <SelectValue placeholder={predictForm.city ? "Pilih Kecamatan" : "Pilih Kota Terlebih Dahulu"} />
                      </SelectTrigger>
                      <SelectContent>
                        {predictForm.city && CITY_DISTRICT_MAP[predictForm.city]?.map((district) => (
                          <SelectItem key={district} value={district}>
                            {district}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="col-span-1 sm:col-span-2 pt-4">
                    {/* Penyesuaian: Button Prediksi diperbesar (h-12) */}
                    <Button type="submit" disabled={isPredicting} className="w-full h-12 text-base">
                      {isPredicting ? "Memproses..." : "Prediksi Harga Sekarang"}
                    </Button>
                  </div>
                </form>

                {predictError && (
                  <div className="mt-6 rounded-md border border-destructive/40 bg-destructive/5 p-4 text-sm text-destructive">
                    {predictError}
                  </div>
                )}

                {predictionResult !== null && (
                  <div className="mt-6 rounded-md border border-green-500/40 bg-green-500/10 p-6 text-center">
                    <p className="text-sm text-muted-foreground mb-1">Estimasi Harga Rumah</p>
                    <h3 className="text-3xl font-bold">Rp {predictionResult.toLocaleString("id-ID")}</h3>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* TAB 2: TRAINING */}
          <TabsContent value="train" className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle>Training Model</CardTitle>
                <CardDescription>Latih ulang model Random Forest dan KMeans di background.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-5 border rounded-lg bg-muted/30">
                  <div>
                    <h4 className="font-semibold">Status Saat Ini</h4>
                    <span className={`text-sm font-medium ${trainingStatus?.status === 'RUNNING' ? 'text-blue-500' : 'text-muted-foreground'}`}>
                      {trainingStatus?.status || "Tidak Diketahui"}
                    </span>
                  </div>
                  <Button variant="outline" size="sm" onClick={checkStatus}>Refresh</Button>
                </div>

                {trainMessage && (
                  <div className="rounded-md border border-primary/40 bg-primary/5 p-4 text-sm">
                    {trainMessage}
                  </div>
                )}
              </CardContent>
              <CardFooter>
                {/* Penyesuaian: Button Training diperbesar (h-12) */}
                <Button
                  onClick={handleTrainModel}
                  disabled={isTrainingLoading || trainingStatus?.status === "RUNNING"}
                  className="w-full h-12 text-base"
                >
                  {isTrainingLoading ? "Mengirim Permintaan..." : "Mulai Pipeline Training"}
                </Button>
              </CardFooter>
            </Card>
          </TabsContent>

          {/* TAB 3: HISTORY */}
          <TabsContent value="history" className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle>Riwayat Prediksi</CardTitle>
                <CardDescription>Daftar riwayat prediksi harga rumah yang telah dilakukan.</CardDescription>
              </CardHeader>
              <CardContent>
                {history.length === 0 ? (
                  <div className="py-10 text-center border-2 border-dashed rounded-lg">
                    <p className="text-sm text-muted-foreground">Belum ada riwayat prediksi.</p>
                  </div>
                ) : (
                  <div className="rounded-md border overflow-hidden">
                    <table className="w-full text-sm">
                      <thead className="bg-muted">
                        <tr>
                          <th className="px-4 py-3 text-left">Lokasi</th>
                          <th className="px-4 py-3 text-right">Hasil</th>
                        </tr>
                      </thead>
                      <tbody>
                        {history.map((item) => (
                          <tr key={item.id} className="border-t">
                            <td className="px-4 py-3">
                              <div className="font-medium">{item.district}</div>
                              <div className="text-xs text-muted-foreground">{item.timestamp}</div>
                            </td>
                            <td className="px-4 py-3 text-right font-bold">
                              Rp {item.predicted_price.toLocaleString("id-ID")}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </>
  );
}