<template>
  <div>
    <div style="display:flex;align-items:center;gap:6px;margin-bottom:14px;font-size:13px;color:var(--color-text-muted)">
      <router-link to="/" style="color:var(--color-text-muted);text-decoration:none">首页</router-link><span>/</span><span>{{ currentCategory || '全部商品' }}</span>
    </div>

    <el-card style="margin-bottom:14px">
      <el-row :gutter="10" align="middle">
        <el-col :xs="24" :sm="6"><el-input v-model="keyword" placeholder="搜索商品" :prefix-icon="Search" clearable size="default" @keyup.enter="doSearch" @clear="doSearch" /></el-col>
        <el-col :xs="12" :sm="4"><el-select v-model="currentCategory" placeholder="全部分类" clearable size="default" style="width:100%" @change="doSearch"><el-option v-for="c in cats" :key="c" :label="c" :value="c" /></el-select></el-col>
        <el-col :xs="12" :sm="4"><el-select v-model="currentSort" placeholder="排序" size="default" style="width:100%" @change="doSearch"><el-option label="默认" value="" /><el-option label="价格低到高" value="price_asc" /><el-option label="价格高到低" value="price_desc" /><el-option label="销量优先" value="sales" /></el-select></el-col>
        <el-col :xs="24" :sm="6" style="margin-top:4px"><el-input v-model="minPrice" placeholder="最低价" size="default" style="width:90px" clearable @change="doSearch" @clear="doSearch" /><span style="margin:0 4px;color:var(--color-text-dim)">-</span><el-input v-model="maxPrice" placeholder="最高价" size="default" style="width:90px" clearable @change="doSearch" @clear="doSearch" /></el-col>
        <el-col :xs="0" :sm="4" style="text-align:right"><span v-if="total>=0" style="font-size:12px;color:var(--color-text-muted)">共{{total}}件</span><el-button v-if="userStore.isAdmin" type="primary" size="small" @click="openAdd" style="margin-left:8px">添加商品</el-button></el-col>
      </el-row>
    </el-card>

    <div v-if="errorMsg" style="padding:40px 0;text-align:center;color:var(--color-danger)">{{ errorMsg }}</div>

    <div v-loading="loading" v-else>
      <div v-if="!loading && list.length === 0" style="padding:80px 0;text-align:center">
        <p style="color:var(--color-text-muted)">没有匹配的商品</p>
        <el-button @click="resetAll">清除筛选</el-button>
      </div>
      <el-row :gutter="14" v-else>
        <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="p in list" :key="p.product_id">
          <div class="pcard" @click="$router.push(`/products/${p.product_id}`)">
            <div class="pc-img">{{ icons[(p.product_id-1) % icons.length] }}</div>
            <div class="pc-name" :title="p.product_name">{{ p.product_name }}</div>
            <div class="pc-cat">{{ p.category }}<span v-if="p.sales_count"> · 已售{{p.sales_count}}</span></div>
            <div class="pc-row">
              <span class="pc-price">¥{{ p.unit_price }}</span>
              <span class="pc-stock" :style="{color:p.stock_quantity>10?'var(--color-success)':p.stock_quantity>0?'var(--color-warning)':'var(--color-danger)'}">{{ p.stock_quantity>10?'有货':p.stock_quantity>0?`仅剩${p.stock_quantity}件`:'缺货' }}</span>
            </div>
            <el-button v-if="!userStore.isAdmin && p.stock_quantity>0" type="primary" size="small" @click.stop="addCart(p.product_id)" style="width:100%;margin-top:10px">加入购物车</el-button>
            <el-button v-if="!userStore.user && p.stock_quantity>0" type="primary" size="small" @click.stop="$router.push('/login')" style="width:100%;margin-top:10px">登录后购买</el-button>
            <el-button v-if="userStore.isAdmin" size="small" @click.stop="openEdit(p)" style="width:100%;margin-top:10px">编辑</el-button>
            <el-button v-if="!userStore.isAdmin && p.stock_quantity<=0" disabled size="small" style="width:100%;margin-top:10px">暂时缺货</el-button>
          </div>
        </el-col>
      </el-row>
      <div style="text-align:center;margin-top:24px" v-if="totalPages>1">
        <el-pagination background layout="prev, pager, next" :total="total" :page-size="pageSize" v-model:current-page="page" @current-change="goPage" />
      </div>
    </div>

    <el-dialog v-model="dlg" :title="editProd?'编辑商品':'添加商品'" width="480px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="商品名称"><el-input v-model="form.product_name" /></el-form-item>
        <el-form-item label="分类"><el-select v-model="form.category"><el-option v-for="c in cats" :key="c" :label="c" :value="c" /></el-select></el-form-item>
        <el-form-item label="厂家"><el-select v-model="form.manufacturer_id"><el-option v-for="m in mfrs" :key="m.manufacturer_id" :label="m.manufacturer_name" :value="m.manufacturer_id" /></el-select></el-form-item>
        <el-form-item label="单价"><el-input-number v-model="form.unit_price" :min="0" :precision="2" /></el-form-item>
        <el-form-item label="库存"><el-input-number v-model="form.stock_quantity" :min="0" /></el-form-item>
        <el-form-item label="预警值"><el-input-number v-model="form.min_stock_threshold" :min="0" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" rows="2" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dlg=false">取消</el-button><el-button type="primary" @click="saveProd" :loading="saving">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { useUserStore } from '@/stores/user'
import { ElMessage, Search } from 'element-plus'

const route = useRoute(); const router = useRouter(); const userStore = useUserStore()
const list = ref([]); const keyword = ref(''); const currentCategory = ref(''); const currentSort = ref('')
const minPrice = ref(''); const maxPrice = ref(''); const loading = ref(false); const errorMsg = ref('')
const total = ref(0); const page = ref(1); const pageSize = 12; const totalPages = ref(1)
const cats = ['球类','服装','器材','鞋类','配件']; const icons = ['🏀','⚽','🏸','👕','⚾','🏐','🏓','🎽','🩳','🧢']
const dlg = ref(false); const editProd = ref(null); const saving = ref(false)
const form = ref({product_name:'',category:'球类',manufacturer_id:1,unit_price:0,stock_quantity:0,min_stock_threshold:10,description:''})
const mfrs = ref([])

const load = async (pg) => {
  loading.value = true; errorMsg.value = ''
  try {
    const params = { page: pg || page.value, page_size: pageSize }
    if (currentCategory.value) params.category = currentCategory.value
    if (currentSort.value) params.sort = currentSort.value
    const mn = parseFloat(minPrice.value); const mx = parseFloat(maxPrice.value)
    if (!isNaN(mn)) params.min_price = mn
    if (!isNaN(mx)) params.max_price = mx
    if (keyword.value) params.keyword = keyword.value
    const url = keyword.value ? '/api/products/search/' : '/api/products/'
    const res = await axios.get(url, { params })
    if (res.data && res.data.items) {
      list.value = res.data.items; total.value = res.data.total || 0; totalPages.value = res.data.total_pages || 1
    } else if (Array.isArray(res.data)) {
      list.value = res.data; total.value = res.data.length; totalPages.value = 1
    } else {
      list.value = []; total.value = 0; errorMsg.value = '数据格式异常'
    }
  } catch (e) {
    console.error('Products load error:', e)
    list.value = []; total.value = 0; errorMsg.value = '加载失败: ' + (e.response?.data?.detail || e.message || '未知错误')
  } finally { loading.value = false }
}

let timer = null
const doSearch = () => { page.value = 1; clearTimeout(timer); timer = setTimeout(() => load(1), 300) }
const goPage = (p) => { page.value = p; load(p) }
const resetAll = () => { keyword.value = ''; currentCategory.value = ''; currentSort.value = ''; minPrice.value = ''; maxPrice.value = ''; errorMsg.value = ''; page.value = 1; load(1) }

const addCart = async (pid) => {
  if (!userStore.user) { ElMessage.warning('请先登录'); router.push('/login'); return }
  try { await axios.post(`/api/cart/${userStore.user.customer_id}/add`, null, { params: { product_id: pid, quantity: 1 } }); ElMessage.success('已加入购物车') } catch { ElMessage.error('添加失败') }
}
const openAdd = () => { editProd.value = null; form.value = {product_name:'',category:'球类',manufacturer_id:1,unit_price:0,stock_quantity:0,min_stock_threshold:10,description:''}; dlg.value = true }
const openEdit = (p) => { editProd.value = p; form.value = {...p}; dlg.value = true }
const saveProd = async () => {
  saving.value = true
  try {
    if (editProd.value) { await axios.put(`/api/admin/products/${editProd.value.product_id}`, form.value); ElMessage.success('更新成功') }
    else { await axios.post('/api/admin/products', form.value); ElMessage.success('添加成功') }
    dlg.value = false; load(page.value)
  } catch { ElMessage.error('保存失败') } finally { saving.value = false }
}

onMounted(() => {
  if (route.query.category) currentCategory.value = route.query.category
  if (route.query.sort) currentSort.value = route.query.sort
  load(1)
  if (userStore.isAdmin) axios.get('/api/admin/manufacturers').then(r => mfrs.value = r.data).catch(() => {})
})
</script>

<style scoped>
.pcard { background:#fff; border:1px solid var(--color-border-light); border-radius:var(--radius-sm); padding:16px; cursor:pointer; transition:all 0.2s; margin-bottom:14px; text-align:center; }
.pcard:hover { border-color:var(--color-primary); box-shadow:var(--shadow-md); transform:translateY(-1px); }
.pc-img { font-size:48px; padding:8px 0; }
.pc-name { font-size:14px; font-weight:600; margin-bottom:4px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.pc-cat { font-size:12px; color:var(--color-text-muted); margin-bottom:8px; }
.pc-row { display:flex; justify-content:space-between; align-items:baseline; margin-bottom:4px; }
.pc-price { font-size:18px; font-weight:700; color:var(--color-accent); }
.pc-stock { font-size:11px; }
</style>
