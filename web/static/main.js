// Entry point: registers the pages (loaded on first visit) and starts the router.
import { $, isStatic, lazy, start } from './core.js';

lazy({
  home: () => import('./home.js'),
  blog: () => import('./blog.js'),
  post: () => import('./blog.js'),
  how: () => import('./how.js'),
  router: () => import('./router.js'),
  code: () => import('./code.js'),
  about: () => import('./about.js'),
});
$('#mode').textContent = isStatic()
  ? 'static site: the blog read-only, exported from the demo database'
  : 'local app: the live Django blog is at /django/';
start();
