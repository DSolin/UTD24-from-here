import { createRouter, createWebHistory } from "vue-router";
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path:"/",component:()=>import("@/components/layout/AppLayout.vue"),children:[
      { path:"",name:"home",component:()=>import("@/views/DashboardView.vue") },
      { path:"dashboard",name:"dashboard",component:()=>import("@/views/DashboardView.vue") },
      { path:"literature",name:"literature",component:()=>import("@/views/LiteratureView.vue") },
      { path:"search",name:"search",component:()=>import("@/views/SearchView.vue") },
      { path:"article/:id",name:"article-detail",component:()=>import("@/views/ArticleDetailView.vue") },
      { path:"favorites",name:"favorites",component:()=>import("@/views/FavoritesView.vue") },
      { path:"settings",name:"settings",component:()=>import("@/views/SettingsView.vue") },
    ]},
    { path:"/login",name:"login",component:()=>import("@/views/LoginView.vue") },
    { path:"/register",name:"register",component:()=>import("@/views/RegisterView.vue") },
  ],
});
export default router;
