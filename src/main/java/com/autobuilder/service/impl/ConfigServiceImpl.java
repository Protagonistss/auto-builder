package com.autobuilder.service.impl;

import com.autobuilder.service.ConfigService;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.charset.StandardCharsets;

@Service
public class ConfigServiceImpl implements ConfigService {

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    public JsonNode parseConfig(MultipartFile file) {
        if (file.isEmpty()) {
            throw new IllegalArgumentException("File cannot be empty");
        }

        try {
            String content = new String(file.getBytes(), StandardCharsets.UTF_8);
            return objectMapper.readTree(content);
        } catch (IOException e) {
            throw new RuntimeException("Failed to parse configuration file: " + e.getMessage(), e);
        }
    }
}
