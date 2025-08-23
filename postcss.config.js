import purgecssModule from '@fullhuman/postcss-purgecss';
const purgecss = purgecssModule.default;

export default {
  plugins: [
    purgecss({
      content: ['./src/**/*.tsx', './src/**/*.html'],
      defaultExtractor: content => content.match(/[\w-/:]+(?<!:)/g) || []
    })
  ]
};