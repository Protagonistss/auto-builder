package com.autobuilder.service.impl;

import ai.z.openapi.ZhipuAiClient;
import ai.z.openapi.service.model.*;
import com.autobuilder.config.AiProperties;
import com.autobuilder.service.LlmService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

import java.util.Arrays;

@Service
@ConditionalOnProperty(name = "ai.active-provider", havingValue = "zhipu")
public class ZhipuLlmServiceImpl implements LlmService {

    private static final Logger logger = LoggerFactory.getLogger(ZhipuLlmServiceImpl.class);

    @Autowired
    private AiProperties aiProperties;

    @Override
    public String generatePlan(String prompt) {
        AiProperties.ZhipuConfig config = aiProperties.getProviders().getZhipu();
        
        if (config == null || config.getApiKey() == null || config.getApiKey().trim().isEmpty()) {
            throw new IllegalStateException("智谱AI配置不完整，请检查API密钥配置");
        }

        try {
            logger.info("Starting to use ZhipuAI to generate build plan, model: {}", config.getModel());
            
            // 初始化智谱AI客户端
            ZhipuAiClient client = ZhipuAiClient.builder().ofZHIPU()
                .apiKey(config.getApiKey())
                .build();
            
            // 注意：根据文档，base URL已经由ofZHIPU()自动设置为智谱AI的地址
            // 如果需要自定义URL，可能需要使用不同的builder方法
            
            // 创建聊天完成请求
            ChatCompletionCreateParams request = ChatCompletionCreateParams.builder()
                .model(config.getModel())
                .messages(Arrays.asList(
                    ChatMessage.builder()
                        .role(ChatMessageRole.USER.value())
                        .content(prompt)
                        .build()
                ))
                .stream(false)
                .temperature(0.3f)
                .maxTokens(4096)
                .build();
            
            // 发送请求并获取响应
            ChatCompletionResponse response = client.chat().createChatCompletion(request);
            
            // 验证响应
            if (response == null) {
                throw new RuntimeException("智谱AI服务返回空响应");
            }
            
            if (!response.isSuccess()) {
                throw new RuntimeException("智谱AI API调用失败: " + response.getMsg());
            }
            
            if (response.getData() == null || response.getData().getChoices() == null || response.getData().getChoices().isEmpty()) {
                throw new RuntimeException("智谱AI返回的数据格式异常：缺少choices数据");
            }
            
            // 提取AI回复内容
            Object contentObj = response.getData().getChoices().get(0).getMessage().getContent();
            if (contentObj == null) {
                throw new RuntimeException("智谱AI返回的内容为空");
            }
            
            String result = contentObj.toString();
            
            if (result.trim().isEmpty()) {
                throw new RuntimeException("智谱AI返回的内容为空字符串");
            }
            
            logger.info("ZhipuAI build plan generation completed, response length: {}", result.length());
            return result;
            
        } catch (Exception e) {
            logger.error("ZhipuAI build plan generation failed, model: {}, error details: {}", config.getModel(), e.getMessage(), e);
            
            // 根据异常类型提供更具体的错误信息
            String errorMessage;
            if (e.getMessage() != null && e.getMessage().contains("401")) {
                errorMessage = "智谱AI API密钥无效或已过期，请检查API Key配置";
            } else if (e.getMessage() != null && e.getMessage().contains("429")) {
                errorMessage = "智谱AI API调用频率超限，请稍后重试";
            } else if (e.getMessage() != null && e.getMessage().contains("timeout")) {
                errorMessage = "智谱AI服务请求超时，请检查网络连接或稍后重试";
            } else if (e.getMessage() != null && e.getMessage().contains("connection")) {
                errorMessage = "无法连接到智谱AI服务，请检查网络连接";
            } else {
                errorMessage = "智谱AI服务异常: " + e.getMessage();
            }
            
            throw new RuntimeException(errorMessage, e);
        }
    }

    @Override
    public String getProviderName() {
        return "Zhipu AI";
    }

    @Override
    public boolean isAvailable() {
        AiProperties.ZhipuConfig config = aiProperties.getProviders().getZhipu();
        return config != null && 
               config.getApiKey() != null && 
               !config.getApiKey().trim().isEmpty() &&
               config.getModel() != null &&
               !config.getModel().trim().isEmpty();
    }
}