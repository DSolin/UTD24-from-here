import axios from 'axios'

const api = axios.create({ baseURL: '/api/v1', timeout: 30000 })

// 自动附带 token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export const getArticles = (params: any) => api.get('/articles', { params })
export const getArticle = (id: string) => api.get(`/articles/${id}`)
export const getBISummary = (params?: any) => api.get('/bi/summary', { params })
export const getWordCloud = (limit = 80, days = 9999, params?: any) => api.get('/bi/wordcloud', { params: { limit, days, ...params } })
export const getCountries = (params?: any) => api.get('/bi/countries', { params })
export const getTrends = (months = 12, params?: any) => api.get('/bi/trends', { params: { months, ...params } })
export const getTopAuthors = (limit = 20, days = 9999, params?: any) => api.get('/bi/top-authors', { params: { limit, days, ...params } })
export const getAuthorTrend = (authorId: string, months = 24) => api.get('/bi/author-trend', { params: { author_id: authorId, months } })
export const getTopJournals = (params?: any) => api.get('/bi/top-journals', { params })
export const getAuthorNetwork = (limit = 50, country?: string, keyword?: string) => api.get('/bi/author-network', { params: { limit, country, keyword } })
export const getJournalsStats = () => api.get('/bi/journals-stats')
export const register = (data: any) => api.post('/auth/register', data)
export const login = (data: any) => api.post('/auth/login', data)

// Favorites
export const getFavorites = () => api.get('/favorites')
export const addFavorite = (articleId: string) => api.post(`/favorites/${articleId}`)
export const removeFavorite = (articleId: string) => api.delete(`/favorites/${articleId}`)
export const checkFavorite = (articleId: string) => api.get(`/favorites/check/${articleId}`)

// Crawler
export const triggerCrawl = (days = 30) => api.post(`/crawler/trigger?days=${days}`)
export const getCrawlStatus = () => api.get('/crawler/status')
