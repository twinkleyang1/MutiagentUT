package com.hmdp.service.impl;

import cn.hutool.core.bean.BeanUtil;
import cn.hutool.core.util.BooleanUtil;
import cn.hutool.core.util.StrUtil;
import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.hmdp.dto.Result;
import com.hmdp.entity.Shop;
import com.hmdp.mapper.ShopMapper;
import com.hmdp.service.IShopService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.hmdp.utils.CacheClient;
import com.hmdp.utils.RedisConstants;
import com.hmdp.utils.RedisData;
import com.hmdp.utils.SystemConstants;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.geo.Distance;
import org.springframework.data.geo.GeoResult;
import org.springframework.data.geo.GeoResults;
import org.springframework.data.redis.connection.RedisGeoCommands;

import java.util.Collections;
import java.util.List;
import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

/**
 * Unit tests for ShopServiceImpl
 */
@ExtendWith(MockitoExtension.class)
@DisplayName("Tests for ShopServiceImpl")
class ShopServiceImplTest {

    @Mock
    private ShopMapper shopMapper;

    @Mock
    private StringRedisTemplate stringRedisTemplate;

    @Mock
    private CacheClient cacheClient;

    @InjectMocks
    private ShopServiceImpl shopService;

    private Shop testShop;

    @BeforeEach
    void setUp() {
        testShop = new Shop();
        testShop.setId(1L);
        testShop.setName("Test Shop");
        testShop.setTypeId(1);
    }

    @Test
    @DisplayName("Should return shop when id is valid and found in cache")
    void shouldReturnShopWhenIdValidAndFoundInCache() {
        // Arrange
        when(cacheClient.queryWithLogicalExpire(
            eq(RedisConstants.CACHE_SHOP_KEY),
            eq(1L),
            eq(Shop.class),
            any(),
            eq(RedisConstants.CACHE_SHOP_TTL),
            eq(TimeUnit.MINUTES)
        )).thenReturn(testShop);

        // Act
        Result result = shopService.queryById(1L);

        // Assert
        assertNotNull(result);
        assertTrue(result.isSuccess());
        assertEquals(testShop, result.getData());
    }

    @Test
    @DisplayName("Should return fail when shop not found")
    void shouldReturnFailWhenShopNotFound() {
        // Arrange
        when(cacheClient.queryWithLogicalExpire(
            anyString(),
            anyLong(),
            any(),
            any(),
            anyLong(),
            any()
        )).thenReturn(null);

        // Act
        Result result = shopService.queryById(999L);

        // Assert
        assertNotNull(result);
        assertFalse(result.isSuccess());
        assertEquals("店铺不存在！", result.getMsg());
    }

    @Test
    @DisplayName("Should update shop and delete cache")
    void shouldUpdateShopAndDeleteCache() {
        // Arrange
        when(shopMapper.updateById(any(Shop.class))).thenReturn(true);
        when(stringRedisTemplate.delete(anyString())).thenReturn(true);

        Shop shopToUpdate = new Shop();
        shopToUpdate.setId(1L);
        shopToUpdate.setName("Updated Shop");

        // Act
        Result result = shopService.update(shopToUpdate);

        // Assert
        assertNotNull(result);
        assertTrue(result.isSuccess());
        verify(shopMapper).updateById(shopToUpdate);
        verify(stringRedisTemplate).delete(RedisConstants.CACHE_SHOP_KEY + 1L);
    }

    @Test
    @DisplayName("Should return fail when update with null id")
    void shouldReturnFailWhenUpdateWithNullId() {
        // Arrange
        Shop shopWithoutId = new Shop();
        shopWithoutId.setName("Test");

        // Act
        Result result = shopService.update(shopWithoutId);

        // Assert
        assertNotNull(result);
        assertFalse(result.isSuccess());
        assertEquals("店铺id不能为空", result.getMsg());
    }

    @Test
    @DisplayName("Should return shops when querying by type without location")
    void shouldReturnShopsWhenQueryByTypeWithoutLocation() {
        // Arrange
        Page<Shop> mockPage = new Page<>(1, 10);
        mockPage.setRecords(Collections.singletonList(testShop));
        when(shopMapper.selectPage(any(Page.class), any())).thenReturn(null);
        when(shopService.query().eq(anyString(), any())).thenReturn(mockPage);
        when(shopService.query().eq(anyString(), any()).page(any(Page.class))).thenReturn(mockPage);

        // Act
        Result result = shopService.queryShopByType(1, 1, null, null);

        // Assert
        assertNotNull(result);
        assertTrue(result.isSuccess());
    }
}