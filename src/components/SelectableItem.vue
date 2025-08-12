<template>
  <div 
    class="selectable-item" 
    :class="{ 
      'selected': modelValue, 
      'has-image': showImage && item.image 
    }"
    @click="toggleSelect"
  >
    <div v-if="showImage && item.image" class="item-image">
      <img :src="item.image" :alt="item.name">
    </div>
    
    <div class="item-content">
      <div class="item-name">{{ item.name }}</div>
      <div v-if="showCategory && item.category" class="item-category">{{ item.category }}</div>
    </div>
    
    <div class="item-indicator">
      <i :class="modelValue ? 'el-icon-check' : 'el-icon-plus'"></i>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SelectableItem',
  props: {
    item: {
      type: Object,
      required: true
    },
    modelValue: {
      type: Boolean,
      default: false
    },
    showImage: {
      type: Boolean,
      default: true
    },
    showCategory: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue', 'change'],
  setup(props, { emit }) {
    const toggleSelect = () => {
      emit('update:modelValue', !props.modelValue);
      emit('change', { item: props.item, selected: !props.modelValue });
    };
    
    return {
      toggleSelect
    };
  }
};
</script>

<style scoped>
.selectable-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-radius: 8px;
  background-color: var(--card-bg);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 8px;
  border: 2px solid transparent;
}

.selectable-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.selectable-item.selected {
  border-color: var(--primary-color);
  background-color: rgba(66, 185, 131, 0.1);
}

.selectable-item.has-image {
  padding: 0;
  overflow: hidden;
}

.item-image {
  width: 60px;
  height: 60px;
  overflow: hidden;
  border-radius: 6px 0 0 6px;
  flex-shrink: 0;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-content {
  flex-grow: 1;
  padding: 10px;
}

.item-name {
  font-weight: 500;
  color: var(--text-color);
}

.item-category {
  font-size: 0.8rem;
  color: var(--text-color);
  opacity: 0.6;
  margin-top: 4px;
}

.item-indicator {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: var(--primary-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
  transition: transform 0.3s ease;
}

.selected .item-indicator {
  transform: scale(1.2);
}
</style> 