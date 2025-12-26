package com.autobuilder.service;

import com.fasterxml.jackson.databind.JsonNode;
import org.springframework.web.multipart.MultipartFile;

public interface ConfigService {
    JsonNode parseConfig(MultipartFile file);
}
