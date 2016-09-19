const fs               = require('fs');
const zlib             = require('zlib');
const spawn            = require('child_process').spawn;
const spawnSync        = require('child_process').spawnSync;

var root_path = __dirname + '/split';

//const compression_level = zlib.Z_NO_COMPRESSION;
//const compression_level = zlib.Z_BEST_SPEED;
//const compression_level = zlib.Z_BEST_COMPRESSION;
const compression_level = zlib.Z_DEFAULT_COMPRESSION;

// Remove previous stuff if any and create root_path
spawnSync('rm', ['-R', root_path]);
fs.existsSync(root_path) || fs.mkdirSync(root_path);

var in_progress = false;

function process_file(file) {
    var chromosome = file.split('.')[0];
    if (chromosome != (chromosome|0)) throw new Error('File name ' + file + ' doesn\'t seem to follow the usual scheme');

    console.log('Processing chromosome ' + chromosome);

    in_progress = true;

    var lineReader = require('readline').createInterface({
        input: require('fs').createReadStream(file)
    });

    var lines = 0;
    var comments = [];
    var columns  = null;
    var data     = [];
    var persons  = [];
    var meta_columns = [];
    var wstreams = {};
    var gzlibs = {};
    var main_path = root_path + '/' + chromosome;
    fs.existsSync(main_path) || fs.mkdirSync(main_path);
    // Remove all folder content

    function iteratePersons(func) {
        for (var i=0, n=persons.length; i<n; i++) {
            func(persons[i], i);
        }
    }

    function createFiles() {
        iteratePersons(function(p) {
            var path = main_path + '/' + p + '.txt';
            if (compression_level !== zlib.Z_NO_COMPRESSION) {
                path += '.gz';
            }
            var wstream = fs.createWriteStream(path);
            wstreams[p] = wstream;

            gzlibs[p] = zlib.createGzip({level: compression_level});
            gzlibs[p].pipe(wstreams[p]);

            gzlibs[p].on('end', function() {
                wstreams[p].end();
            });
        });

        var path = main_path + '/_meta.txt';
        if (compression_level !== zlib.Z_NO_COMPRESSION) {
            path += '.gz';
        }
        wstreams.meta = fs.createWriteStream(path);

        gzlibs.meta = zlib.createGzip({level: compression_level});
        gzlibs.meta.pipe(wstreams.meta);
        gzlibs.meta.on('end', function() {
            wstreams.meta.end();
        });

        console.log(persons.length + ' individual files created');
    }

    function writeComments() {
        var str = comments.join('\n') + '\n';
        var wstream = fs.createWriteStream(main_path + '/_comments.txt');
        wstream.write(str);
        wstream.end();
        console.log('Comments written');
    }

    function writeHeaders() {
        var str = meta_columns.join('\t') + '\n';
        gzlibs.meta.write(str);
        console.log('Headers written');
    }

    function closeFiles() {
        iteratePersons(function(p) {
            gzlibs[p].end();
        });
        gzlibs.meta.end();
    }

    function flushToDisk() {
        //var records = data.length;
        if (records == 0) {
            console.log('No data to flush to disk');
        }
        //console.log('Flushing ' + records + ' records to disk for ' + persons.length + ' samples');

        var lines = [];
        iteratePersons(function(p, idx) {
            lines[idx] = [];
        });
        var meta = [];
        for (var r=0; r<records; r++) {
            var els = data[r].split('\t');
            if (els.length !== column_count) {
                throw new Error('Column count mismatch at line ' + line + ' (expected: ' + column_count + ', got: ' + els.length + ')');
            }

            var meta_str = '';
            for (var i=0, n=meta_columns.length; i<n; i++) {
                meta_str += els[i] + '\t';
            }
            meta[r] = meta_str;
            iteratePersons(function(p, idx) {
                lines[idx][r] = els[idx + meta_columns.length];
            });
        }
        gzlibs.meta.write(meta.join('\n') + '\n');
        //gzlibs.meta.flush();

        iteratePersons(function(p, idx) {
            gzlibs[p].write(lines[idx].join('\n') + '\n');
            //gzlibs[p].flush();
        });

        //data = [];
        records = 0;
    }
    var t0 = new Date();
    var start_time = t0;
    var batch = 1000;
    var records = 0;
    var total_recs = 0;
    var column_count = 0;
    lineReader.on('line', function (line) {
        if (line.substring(0, 2) == '##') {
            // Comment
            comments.push(line);
            console.log('comment: ' + line);
        } else if (line.substring(0, 1) == '#') {
            // Columns
            columns = line.split('\t');
            column_count = columns.length;
            console.log('File has ' + column_count + ' columns');
            // Prepare arrays for data
            var meta_end = false;
            for (var i=0, n=column_count; i<n; i++) {
                var col_name = columns[i];
                if (!meta_end) {
                    if (col_name.indexOf('_') !== -1) {
                        meta_end = true;
                        console.log('meta columns: ' + meta_columns.length);
                    } else {
                        console.log('meta column: ' + col_name);
                        meta_columns.push(col_name);
                    }
                }
                if (meta_end) persons.push(col_name);
            }
            createFiles();
            writeComments();
            writeHeaders();
        } else {
            data[records] = line;
            records++;
            total_recs++;
        }
        lines++;

        /*
        if (lines % 100 === 0) {
            closeFiles();
            throw new Error('THE END');
        }*/
        if (total_recs > 0 && total_recs % batch === 0) {
            var t = new Date() - t0;
            //console.log('Time to read  ', batch + ': ', t, '(' + (t / batch) + ' ms per record)');
            t0 = new Date();
            flushToDisk();
            t = new Date() - t0;
            //console.log('Time to write ', batch + ': ', t, '(' + (t / batch) + ' ms per record)');
            t0 = new Date();
            //console.log(total_recs + ' Average time per 1000 record: ' + Math.round((t0 - start_time) / total_recs * 1000) + ' ms');
            process.stdout.write('\r' + total_recs + ' records. Average time per 1000 records: ' + Math.round((t0 - start_time) / total_recs * 1000) + ' ms  ');
            /*if (total_recs > 100000) {
                lineReader.close();
            }*/
        }
    });
    lineReader.on('close', function() {
        flushToDisk();
        closeFiles();
        console.log('Total lines: ' + lines + ', Total records: ' + total_recs);
        // Remove file
        fs.unlink(file);
        in_progress = false;
        check_files();
    });
}

var files = [];
fs.readdirSync(__dirname).forEach(function (name) {
    /*var filePath = path.join(currentDirPath, name);
    var stat = fs.statSync(filePath);
    if (stat.isFile()) {
        callback(filePath, stat);
    } else if (stat.isDirectory()) {
        walkSync(filePath, callback);
    }*/
    if (/.vcf.zip$/.test(name)) {
        console.log('Found ' + name);
        files.push(name);
        check_files();
    }
});

function check_files() {
    if (in_progress) return;

    in_progress = true;
    var name = files.pop();
    if (!name) return; 
    console.log('Unzipping ' + name);
    var p = spawn('unzip', ['-o', name]);
    p.on('close', (code) => {
        // Remove junk from Mac archive, if any
        spawn('rm', ['-R', '__MACOSX']);
        var file = name.replace(/\.zip$/, '');
        if (fs.existsSync(file)) {
            process_file(file);
        } else {
            console.log('Error, unzipped ' + name + ' but cannot find ' + file);
        }
    });
}