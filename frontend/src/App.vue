<template><router-view /></template>
<style>
.page-enter-active,.page-leave-active{transition:opacity .3s ease,transform .3s ease}
.page-enter-from{opacity:0;transform:translateY(12px)}
.page-leave-to{opacity:0;transform:translateY(-12px)}
</style>
