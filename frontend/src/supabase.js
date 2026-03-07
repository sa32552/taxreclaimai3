
import { createClient } from '@supabase/supabase-js'

// Configuration Supabase
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://nevyttqdnanrmxsjozjd.supabase.co'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'sb_publishable_XQugS3Pj77HcKIX-qelwZQ_k7vp7JhJ'

// Création du client Supabase
export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Fonctions d'authentification
export const auth = {
  // Inscription
  async signUp(email, password, metadata = {}) {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: metadata
      }
    })
    return { data, error }
  },

  // Connexion
  async signIn(email, password) {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    })
    return { data, error }
  },

  // Déconnexion
  async signOut() {
    const { error } = await supabase.auth.signOut()
    return { error }
  },

  // Récupération du mot de passe
  async resetPassword(email) {
    const { data, error } = await supabase.auth.resetPasswordForEmail(email)
    return { data, error }
  },

  // Vérification de l'authentification
  async getCurrentUser() {
    const { data: { user } } = await supabase.auth.getUser()
    return user
  },

  // Écoute des changements d'authentification
  onAuthStateChange(callback) {
    return supabase.auth.onAuthStateChange(callback)
  }
}

// Fonctions de stockage
export const storage = {
  // Upload de fichier
  async uploadFile(bucket, path, file) {
    const { data, error } = await supabase.storage
      .from(bucket)
      .upload(path, file)
    return { data, error }
  },

  // Téléchargement de fichier
  async downloadFile(bucket, path) {
    const { data, error } = await supabase.storage
      .from(bucket)
      .download(path)
    return { data, error }
  },

  // Suppression de fichier
  async deleteFile(bucket, path) {
    const { data, error } = await supabase.storage
      .from(bucket)
      .remove([path])
    return { data, error }
  }
}

// Fonctions de base de données
export const database = {
  // Requête SELECT
  async select(table, columns = '*', filter = {}) {
    let query = supabase.from(table).select(columns)

    if (filter.eq) {
      Object.entries(filter.eq).forEach(([key, value]) => {
        query = query.eq(key, value)
      })
    }

    const { data, error } = await query
    return { data, error }
  },

  // Requête INSERT
  async insert(table, data) {
    const { data: result, error } = await supabase
      .from(table)
      .insert(data)
      .select()
    return { data: result, error }
  },

  // Requête UPDATE
  async update(table, data, filter) {
    let query = supabase.from(table).update(data)

    if (filter.eq) {
      Object.entries(filter.eq).forEach(([key, value]) => {
        query = query.eq(key, value)
      })
    }

    const { data: result, error } = await query.select()
    return { data: result, error }
  },

  // Requête DELETE
  async delete(table, filter) {
    let query = supabase.from(table).delete()

    if (filter.eq) {
      Object.entries(filter.eq).forEach(([key, value]) => {
        query = query.eq(key, value)
      })
    }

    const { data, error } = await query.select()
    return { data, error }
  }
}
