package com.hmdp.controller;

import cn.hutool.core.bean.BeanUtil;
import com.hmdp.dto.LoginFormDTO;
import com.hmdp.dto.Result;
import com.hmdp.dto.UserDTO;
import com.hmdp.entity.User;
import com.hmdp.entity.UserInfo;
import com.hmdp.service.IUserInfoService;
import com.hmdp.service.IUserService;
import com.hmdp.utils.UserHolder;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.mock.web.MockHttpSession;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

/**
 * Unit tests for UserController
 */
@ExtendWith(MockitoExtension.class)
@DisplayName("Tests for UserController")
class UserControllerTest {

    @Mock
    private IUserService userService;

    @Mock
    private IUserInfoService userInfoService;

    @Mock
    private StringRedisTemplate redisTemplate;

    @InjectMocks
    private UserController userController;

    private MockHttpSession session;

    @BeforeEach
    void setUp() {
        session = new MockHttpSession();
        UserHolder.removeUser();
    }

    @Test
    @DisplayName("Should send verification code when phone is valid")
    void shouldSendVerificationCodeWhenPhoneIsValid() {
        // Arrange
        String phone = "13800138000";
        when(userService.sendCode(eq(phone), any())).thenReturn(Result.ok());

        // Act
        Result result = userController.sendCode(phone, session);

        // Assert
        assertNotNull(result);
        verify(userService).sendCode(eq(phone), any());
    }

    @Test
    @DisplayName("Should login successfully when credentials are valid")
    void shouldLoginSuccessfullyWhenCredentialsAreValid() {
        // Arrange
        LoginFormDTO loginForm = new LoginFormDTO();
        loginForm.setPhone("13800138000");
        loginForm.setCode("123456");
        UserDTO userDTO = new UserDTO();
        userDTO.setId(1L);
        userDTO.setNickName("testUser");
        when(userService.login(any(LoginFormDTO.class), any())).thenReturn(Result.ok(userDTO));

        // Act
        Result result = userController.login(loginForm, session);

        // Assert
        assertNotNull(result);
        verify(userService).login(any(LoginFormDTO.class), any());
    }

    @Test
    @DisplayName("Should logout successfully and remove user from ThreadLocal")
    void shouldLogoutSuccessfullyAndRemoveUserFromThreadLocal() {
        // Arrange
        UserDTO user = new UserDTO();
        user.setId(1L);
        UserHolder.saveUser(user);

        // Act
        Result result = userController.logout();

        // Assert
        assertNotNull(result);
        assertNull(UserHolder.getUser());
    }

    @Test
    @DisplayName("Should return current user when user is logged in")
    void shouldReturnCurrentUserWhenUserIsLoggedIn() {
        // Arrange
        UserDTO userDTO = new UserDTO();
        userDTO.setId(1L);
        userDTO.setNickName("testUser");
        UserHolder.saveUser(userDTO);

        // Act
        Result result = userController.me();

        // Assert
        assertNotNull(result);
        UserDTO returnedUser = (UserDTO) result.getData();
        assertEquals(1L, returnedUser.getId());
    }

    @Test
    @DisplayName("Should return empty result when user not logged in")
    void shouldReturnEmptyResultWhenUserNotLoggedIn() {
        // Arrange
        UserHolder.removeUser();

        // Act
        Result result = userController.me();

        // Assert
        assertNotNull(result);
        assertNull(result.getData());
    }

    @Test
    @DisplayName("Should return user info when user exists")
    void shouldReturnUserInfoWhenUserExists() {
        // Arrange
        Long userId = 1L;
        UserInfo userInfo = new UserInfo();
        userInfo.setId(userId);
        userInfo.setNickName("testInfo");
        when(userInfoService.getById(userId)).thenReturn(userInfo);

        // Act
        Result result = userController.info(userId);

        // Assert
        assertNotNull(result);
        verify(userInfoService).getById(userId);
    }

    @Test
    @DisplayName("Should return ok when user info not found")
    void shouldReturnOkWhenUserInfoNotFound() {
        // Arrange
        Long userId = 999L;
        when(userInfoService.getById(userId)).thenReturn(null);

        // Act
        Result result = userController.info(userId);

        // Assert
        assertNotNull(result);
        assertTrue(result.isSuccess());
    }

    @Test
    @DisplayName("Should return user by id when user exists")
    void shouldReturnUserByIdWhenUserExists() {
        // Arrange
        Long userId = 1L;
        User user = new User();
        user.setId(userId);
        user.setNickName("testUser");
        when(userService.getById(userId)).thenReturn(user);

        // Act
        Result result = userController.queryUserById(userId);

        // Assert
        assertNotNull(result);
        UserDTO userDTO = (UserDTO) result.getData();
        assertEquals(userId, userDTO.getId());
    }

    @Test
    @DisplayName("Should return ok when user not found by id")
    void shouldReturnOkWhenUserNotFoundById() {
        // Arrange
        Long userId = 999L;
        when(userService.getById(userId)).thenReturn(null);

        // Act
        Result result = userController.queryUserById(userId);

        // Assert
        assertNotNull(result);
        assertTrue(result.isSuccess());
    }

    @Test
    @DisplayName("Should sign successfully")
    void shouldSignSuccessfully() {
        // Arrange
        when(userService.sign()).thenReturn(Result.ok());

        // Act
        Result result = userController.sign();

        // Assert
        assertNotNull(result);
        assertTrue(result.isSuccess());
        verify(userService).sign();
    }

    @Test
    @DisplayName("Should return sign count successfully")
    void shouldReturnSignCountSuccessfully() {
        // Arrange
        when(userService.signCount()).thenReturn(Result.ok(5));

        // Act
        Result result = userController.signCount();

        // Assert
        assertNotNull(result);
        assertEquals(5, result.getData());
        verify(userService).signCount();
    }
}
