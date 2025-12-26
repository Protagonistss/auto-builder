package com.autobuilder.service.impl;

import com.autobuilder.service.ConfigService;
import com.autobuilder.service.LlmService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.charset.StandardCharsets;

@Service
public class ConfigServiceImpl implements ConfigService {

    private static final Logger logger = LoggerFactory.getLogger(ConfigServiceImpl.class);
    
    private final ObjectMapper objectMapper = new ObjectMapper();
    
    @Autowired(required = false)
    private LlmService llmService;

    @Override
    public OrmGenerationResult generateOrm(MultipartFile file) {
        if (file.isEmpty()) {
            throw new IllegalArgumentException("File cannot be empty");
        }

        if (llmService == null) {
            throw new IllegalStateException("AI服务不可用，请检查配置");
        }

        try {
            // 读取上传的文件内容
            String configContent = new String(file.getBytes(), StandardCharsets.UTF_8);
            logger.info("开始处理ORM生成请求，文件大小: {} 字节", configContent.length());

            // 读取ORM提示词模板
            String promptTemplate = readOrmPromptTemplate();
            
            // 构建完整的提示词
            String fullPrompt = promptTemplate + "\n\n输入配置:\n" + configContent;

            // 调用AI生成ORM
            String aiResponse = llmService.generatePlan(fullPrompt);
            
            // 解析AI响应，提取ORM XML
            String ormXml = extractOrmXml(aiResponse);
            String entityName = extractEntityName(aiResponse);
            String tableName = extractTableName(aiResponse);

            logger.info("ORM生成完成，实体: {}, 表: {}", entityName, tableName);
            
            return new OrmGenerationResult(ormXml, entityName, tableName);

        } catch (IOException e) {
            throw new RuntimeException("读取文件失败: " + e.getMessage(), e);
        } catch (Exception e) {
            logger.error("ORM生成失败", e);
            throw new RuntimeException("ORM生成失败: " + e.getMessage(), e);
        }
    }

    private String readOrmPromptTemplate() throws IOException {
        ClassPathResource resource = new ClassPathResource("prompts/orm/orm.md");
        if (!resource.exists()) {
            throw new IllegalStateException("ORM提示词模板文件不存在: prompts/orm/orm.md");
        }
        return new String(resource.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
    }

    private String extractOrmXml(String aiResponse) {
        logger.debug("Extracting ORM XML from AI response, response length: {}", aiResponse.length());
        
        // 清理响应，移除可能的代码块标记
        String cleanedResponse = aiResponse.replaceAll("```xml\\s*", "").replaceAll("```\\s*$", "").trim();
        
        // 提取XML部分，优先查找完整的orm标签
        int xmlStart = cleanedResponse.indexOf("<orm");
        if (xmlStart == -1) {
            // 如果没有找到orm标签，尝试查找entities标签
            xmlStart = cleanedResponse.indexOf("<entities");
        }
        
        if (xmlStart == -1) {
            // 如果还没有找到，尝试查找任何XML标签
            xmlStart = cleanedResponse.indexOf("<");
        }
        
        if (xmlStart == -1) {
            logger.warn("AI response does not contain any XML content: {}", cleanedResponse.substring(0, Math.min(200, cleanedResponse.length())));
            throw new RuntimeException("AI response does not contain any XML content, please check the response format of the AI model");
        }
        
        // 查找XML结束标签
        int xmlEnd = cleanedResponse.lastIndexOf("</orm>");
        if (xmlEnd == -1) {
            // 如果没有找到orm结束标签，尝试查找entities结束标签
            xmlEnd = cleanedResponse.lastIndexOf("</entities>");
        }
        
        if (xmlEnd == -1) {
            // 如果还没有找到，尝试查找最后一个>符号
            xmlEnd = cleanedResponse.lastIndexOf(">");
        }
        
        if (xmlEnd == -1 || xmlEnd <= xmlStart) {
            logger.warn("AI response does not contain a complete XML content, start position: {}, end position: {}", xmlStart, xmlEnd);
            throw new RuntimeException("AI response does not contain a complete XML content, please check the response format of the AI model");
        }
        
        String xmlContent = cleanedResponse.substring(xmlStart, xmlEnd + 6); // +6 to include "</orm>" or similar
        logger.debug("Successfully extracted XML content, length: {}", xmlContent.length());
        
        return xmlContent;
    }

    private String extractEntityName(String aiResponse) {
        logger.debug("Extracting entity name from AI response");
        
        // 使用正则表达式提取entity的name属性
        java.util.regex.Pattern pattern = java.util.regex.Pattern.compile("entity\\s+name\\s*=\\s*\"([^\"]+)\"");
        java.util.regex.Matcher matcher = pattern.matcher(aiResponse);
        
        if (matcher.find()) {
            String entityName = matcher.group(1);
            logger.debug("成功提取实体名称: {}", entityName);
            return entityName;
        }
        
        logger.warn("未能从AI响应中提取实体名称，使用默认值");
        return "app.module.Entity";
    }

    private String extractTableName(String aiResponse) {
        logger.debug("Extracting table name from AI response");
        
        // 使用正则表达式提取tableName属性
        java.util.regex.Pattern pattern = java.util.regex.Pattern.compile("tableName\\s*=\\s*\"([^\"]+)\"");
        java.util.regex.Matcher matcher = pattern.matcher(aiResponse);
        
        if (matcher.find()) {
            String tableName = matcher.group(1);
            logger.debug("Successfully extracted table name: {}", tableName);
            return tableName;
        }
        
        logger.warn("Failed to extract table name from AI response, using default value");
        return "entity_table";
    }
}
