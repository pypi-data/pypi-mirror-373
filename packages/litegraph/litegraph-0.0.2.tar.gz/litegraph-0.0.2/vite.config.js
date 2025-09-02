import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
    root: path.resolve(__dirname, 'js'),
    server: {
        watch: {
            paths: [path.resolve(__dirname, 'js')],
        },
    },
    resolve: {
        alias: {
            '@': path.resolve(__dirname, 'js')
        }
    },
    plugins: [tailwindcss(), vue()],
});
