package com.hmdp.controller;

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

import javax.servlet.http.HttpSession;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
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

    @Mock
    private HttpSession session;

    @InjectMocks
    private UserController userController;

    private UserDTO testUserDTO;
    private User testUser;
    private UserInfo testUserInfo;

    @BeforeEach
    void setUp() {
        testUserDTO = new UserDTO();
        testUserDTO.setId(1L);
        testUserDTO.setNickName("TestUser");

        testUser = new User();
        testUser.setId(1L);
        testUser.setNickName("TestUser");

        testUserInfo = new UserInfo();
        testUserInfo.setId(1L);
        testUserInfo.setCity("TestCity");
    }

    @Test
    @DisplayName("Should return result when sendCode is called")
    void shouldReturnResultWhenSendCodeCalled() {
        // Arrange
        when(userService.sendCode(anyString(), any(HttpSession.class))).thenReturn(Result.ok());

        // Act
        Result result = userController.sendCode("13800138000", session);

        // Assert
        assertNotNull(result);
        assertTrue(result.isSuccess());
        verify(userService).sendCode("13800138000", session);
    }

    @Test
    @DisplayName("Should return result when login is called")
    void shouldReturnResultWhenLoginCalled() {
        // Arrange
        LoginFormDTO loginForm = new LoginFormDTO();
        loginForm.setPhone("13800138000");
        loginForm.setCode("123456");
        when(userService.login(any(LoginFormDTO.class), any(HttpSession.class))).thenReturn(Result.ok());

        // Act
        Result result = userController.login(loginForm, session);

        // Assert
        assertNotNull(result);
        assertTrue(result.isSuccess());
    }

    @Test
    @DisplayName("Should return fail when logout is called")
    void shouldReturnFailWhenLogoutCalled() {
        // Act
        Result result = userController.logout();

        // Assert
        assertNotNull(result);
        assertFalse(result.isSuccess());
        assertEquals("功能未完成", result.getMsg());
        verify(UserHolder.class);
    }

    @Test
    @DisplayName("Should return user when me is called and user is logged in")
    void shouldReturnUserWhenMeCalledAndUserLoggedIn() {
        // Arrange
        UserHolder.setUser(testUserDTO);

        // Act
        Result result = userController.me();

        // Assert
        assertNotNull(result);
        assertTrue(result.isSuccess());
        assertEquals(testUserDTO, result.getData());

        // Cleanup
        UserHolder.removeUser();
    }

    @Test
    @DisplayName("Should return user info when info is called")
    void shouldReturnUserInfoWhenInfoCalled() {
        // Arrange
        when(userInfoService.getById(1L)).thenReturn(testUserInfo);

        // Act
        Result result = userController.info(1L);

        // Assert
        assertNotNull(result);
        assertTrue(result.isSuccess());
    }

    @Test
    @DisplayName("Should return empty result when user not found")
    void shouldReturnEmptyResultWhenUserNotFound() {
        // Arrange
        when(userService.getById(999L)).thenReturn(null);

        // Act
        Result result = userController.queryUserById(999L);

        // Assert
        assertNotNull(result);
        assertTrue(result.isSuccess());
    }

    @Test
    @DisplayName("Should return user DTO when user found")
    void shouldReturnUserDTOWhenUserFound() {
        // Arrange
        when(userService.getById(1L)).thenReturn(testUser);

        // Act
        Result result = userController.queryUserById(1L);

        // Assert
        assertNotNull(result);
        assertTrue(result.isSuccess());
        UserDTO returnedUser = (UserDTO) result.getData();
        assertEquals(testUser.getNickName(), returnedUser.getNickName());
    }
}