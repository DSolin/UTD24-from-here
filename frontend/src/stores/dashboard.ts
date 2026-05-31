import { defineStore } from "pinia"
import { ref, computed } from "vue"

export interface BreadcrumbItem {
  type: "country" | "keyword" | "author"
  value: string
  label: string
}

export const useDashboardStore = defineStore("dashboard", () => {
  const filterCountry = ref<string | null>(null)
  const filterKeyword = ref<string | null>(null)
  const filterAuthorId = ref<string | null>(null)
  const filterDateFrom = ref<string | null>(null)
  const filterDateTo = ref<string | null>(null)
  const breadcrumb = ref<BreadcrumbItem[]>([])

  const isDrilledDown = computed(() => breadcrumb.value.length > 0)

  const filterParams = computed(() => ({
    country: filterCountry.value,
    keyword: filterKeyword.value,
    author_id: filterAuthorId.value,
    date_from: filterDateFrom.value,
    date_to: filterDateTo.value,
  }))

  function drillDown(type: "country" | "keyword" | "author", value: string, label: string) {
    breadcrumb.value.push({ type, value, label })
    if (type === "country") filterCountry.value = value
    if (type === "keyword") filterKeyword.value = value
    if (type === "author") filterAuthorId.value = value
  }

  function goToBreadcrumb(index: number) {
    // 回到面包屑第 index 层（0 = All）
    if (index < 0) return
    breadcrumb.value = breadcrumb.value.slice(0, index)
    // 重建 filter 状态
    filterCountry.value = null
    filterKeyword.value = null
    filterAuthorId.value = null
    for (const item of breadcrumb.value) {
      if (item.type === "country") filterCountry.value = item.value
      if (item.type === "keyword") filterKeyword.value = item.value
      if (item.type === "author") filterAuthorId.value = item.value
    }
  }

  function clearAll() {
    breadcrumb.value = []
    filterCountry.value = null
    filterKeyword.value = null
    filterAuthorId.value = null
    filterDateFrom.value = null
    filterDateTo.value = null
  }

  function setDateRange(from: string | null, to: string | null) {
    filterDateFrom.value = from
    filterDateTo.value = to
  }

  return {
    filterCountry, filterKeyword, filterAuthorId, filterDateFrom, filterDateTo,
    breadcrumb, isDrilledDown, filterParams,
    drillDown, goToBreadcrumb, clearAll, setDateRange,
  }
})
