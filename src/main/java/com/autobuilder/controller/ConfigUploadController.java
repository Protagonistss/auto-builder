package com.autobuilder.controller;

import com.autobuilder.service.ConfigService;
import com.fasterxml.jackson.databind.JsonNode;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api")
public class ConfigUploadController {

    private final ConfigService configService;

    public ConfigUploadController(ConfigService configService) {
        this.configService = configService;
    }

    @PostMapping("/upload")
    public ResponseEntity<?> uploadConfig(@RequestParam("file") MultipartFile file) {
        JsonNode jsonNode = configService.parseConfig(file);
        return ResponseEntity.ok().body(jsonNode);
    }
}
