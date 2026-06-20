import { supabase } from "./supabase";

export async function uploadImage(file) {
  const bucket = process.env.NEXT_PUBLIC_SUPABASE_BUCKET;

  const ext = file.name.split(".").pop()?.toLowerCase();
  const fileName = `public/${Date.now()}-${crypto.randomUUID()}.${ext}`;

  const { data, error } = await supabase.storage
    .from(bucket)
    .upload(fileName, file, {
      cacheControl: "3600",
      upsert: false,
      contentType: file.type,
    });

  if (error) throw error;

  const { data: urlData } = supabase.storage
    .from(bucket)
    .getPublicUrl(data.path);

  return urlData.publicUrl;
}