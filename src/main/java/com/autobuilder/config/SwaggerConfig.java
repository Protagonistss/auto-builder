package com.autobuilder.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class SwaggerConfig {

    @Bean
    public OpenAPI autoBuilderOpenAPI() {
        return new OpenAPI()
                .info(new Info().title("Auto Builder API")
                        .description("API documentation for Auto Builder Service")
                        .version("v1.0.0"));
    }
}
