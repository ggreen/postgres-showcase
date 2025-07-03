/*
 *
 *  * Copyright 2023 VMware, Inc.
 *  * SPDX-License-Identifier: GPL-3.0
 *
 */

package showcase.postgres.jdbc.sql.rest.controller;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

/**
 * REST API to execute SQL queries
 * @author gregory green
 */
@RestController
@RequestMapping("sql")
@RequiredArgsConstructor
@Slf4j
public class ExecuteSqlController {

    private final JdbcTemplate jdbcTemplate;

    @PostMapping
    public List<Map<String, Object>> execute(@RequestBody String sql) {



        var input = sql.trim().toLowerCase();
        if(!input.startsWith("select"))
        {
            log.info("Executing update: {}",sql);
            int update = jdbcTemplate.update(sql);
            log.info("Returning update: {}",update);
            return List.of(Map.of("update",update));
        }

        log.info("Executing query SQL: {}",sql);
        return jdbcTemplate.queryForList(sql);
    }
}
