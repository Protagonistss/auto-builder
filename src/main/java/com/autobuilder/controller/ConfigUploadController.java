package com.autobuilder.controller;

import com.autobuilder.common.Result;
import com.autobuilder.service.ConfigService;
import com.fasterxml.jackson.databind.JsonNode;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api")
@Tag(name = "Config Upload", description = "API for uploading and parsing configuration files")
public class ConfigUploadController {

    private final ConfigService configService;

    public ConfigUploadController(ConfigService configService) {
        this.configService = configService;
    }

    @Operation(summary = "Upload configuration file", 
            description = "Uploads a JSON configuration file and returns its parsed content",
            responses = {
                    @ApiResponse(responseCode = "200", description = "File uploaded and parsed successfully"),
                    @ApiResponse(responseCode = "400", description = "Invalid input or file format"),
                    @ApiResponse(responseCode = "500", description = "Internal server error")
            })
    @PostMapping(value = "/upload", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public Result<JsonNode> uploadConfig(
            @Parameter(description = "Configuration file to upload (JSON format)", required = true,
                    content = @Content(mediaType = MediaType.MULTIPART_FORM_DATA_VALUE))
            @RequestParam("file") MultipartFile file) {
        JsonNode jsonNode = configService.parseConfig(file);
        return Result.success(jsonNode);
    }
}
