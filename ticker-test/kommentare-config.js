// Supabase-Zugang für die Kommentare. Beide Werte sind öffentlich gedacht (Publishable Key, früher "anon key").
// Geschützt wird über die Regeln in supabase/kommentare.sql (Row Level Security), nicht über diesen Schlüssel.
// Leer = Kommentarbereich bleibt unsichtbar.
window.WI_KOMMENTARE = {
  url: "",   // z. B. https://abcdefghijklmnop.supabase.co
  key: ""    // Publishable Key aus Project Settings > API Keys
};
